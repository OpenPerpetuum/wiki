#!/usr/bin/env python3
"""fix_tp_coords.py — correct world map TP line coordinates using zone map data.

The world map TP lines (data-tps / data-tpd) use x1,y1 for the TP source
position and x2,y2 for the destination. The .NET generator sometimes uses
the zone center instead of the actual TP position on the island.

This script reads the zone map SVGs (which have the real game coordinates in
2048×2048 space) and rewrites the world map TP line endpoints:
  - x1,y1 (source): from the zone map's exit-line x1,y1, scaled to the
    world map zone's bounding box
  - x2,y2 (destination): from the destination zone's corresponding
    entry-line (or its center if no entry data is available)

Usage: python3 tools/fix_tp_coords.py
"""
import re
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
ZONEMAPS = os.path.join(ROOT, "static", "zonemaps")

ZONE_MAP_SIZE = 2048  # zone map SVGs use viewBox="0 0 2048 2048"


def find_map_files():
    """Find all zones/map.md files across all languages."""
    files = []
    for dirpath, _, filenames in os.walk(CONTENT):
        if "map.md" in filenames and dirpath.endswith("/zones"):
            files.append(os.path.join(dirpath, "map.md"))
    return sorted(files)


def zone_slug_to_file(slug):
    """zone_ASI_A_real → static/zonemaps/zone-asi-a-real.svg"""
    fname = slug.lower().replace("_", "-") + ".svg"
    return os.path.join(ZONEMAPS, fname)


def parse_zone_positions(content):
    """Extract zone positions from world map SVG.
    
    Uses the <path transform="translate(x, y) scale(s, s)"/> that follows each zone's
    <circle> element. The translate gives the zone's top-left corner and scale*256
    gives the width/height.
    
    Returns dict: zone_name → (x, y, w, h)
    """
    positions = {}
    # Match the <a> tag followed by the path transform
    for m in re.finditer(
        r'<a href="/(?:cs/|de/|es/|fr/|it/|ja/|ko/|nl/|pl/|pt/|ru/|zh-CN/|zh-TW/)?zones/([^/]+)/">'
        r'<g><circle cx="([\d.]+)" cy="([\d.]+)"[^>]*>.*?</circle>'
        r'<path transform="translate\(([\d.]+), ([\d.]+)\) scale\(([\d.]+), ([\d.]+)\)"',
        content, re.DOTALL
    ):
        slug = m.group(1).replace("-", "_")
        # Groups: 1=slug, 2=cx, 3=cy, 4=tx, 5=ty, 6=scale_x, 7=scale_y
        x, y = float(m.group(4)), float(m.group(5))
        s = float(m.group(6))
        # The path data is in 256-unit space (thumb.svg viewBox)
        size = s * 256
        w = h = size
        positions[slug] = (x, y, w, h)
    return positions


def get_pos(positions, zone_name):
    """Case-insensitive zone position lookup.
    Position keys are lowercase (from URL slugs), but TP attributes
    may use mixed case (e.g., zone_TM_pvp vs zone_tm_pvp).
    """
    return positions.get(zone_name.lower())


def parse_zone_map_tps(zone_file):
    """Parse exit lines from a zone map SVG.
    
    Returns dict: dest_zone → list of (x1, y1) in 2048×2048 space
    """
    if not os.path.isfile(zone_file):
        return {}
    with open(zone_file, "r", encoding="utf-8") as f:
        data = f.read()
    
    tps = {}
    for m in re.finditer(r'data-tps="(\d+)" data-tpd="([^"]+)" x1="([\d.]+)" y1="([\d.]+)"', data):
        eid, dest, x1, y1 = m.group(1), m.group(2), float(m.group(3)), float(m.group(4))
        if dest not in tps:
            tps[dest] = []
        tps[dest].append((x1, y1))
    return tps


def parse_zone_map_entries(zone_file):
    """Parse entry lines (landing spots) from a zone map SVG.
    
    Returns dict: src_zone → list of (x, y) in 2048×2048 space
    """
    if not os.path.isfile(zone_file):
        return {}
    with open(zone_file, "r", encoding="utf-8") as f:
        data = f.read()
    
    entries = {}
    # Entry lines have data-tps as the source zone name
    for m in re.finditer(r'data-tps="([^"]+)" data-tpd="(\d+)" x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"', data):
        src, eid, x1, y1, x2, y2 = m.group(1), m.group(2), float(m.group(3)), float(m.group(4)), float(m.group(5)), float(m.group(6))
        # The entry point is at x2,y2 (where the player lands)
        if src not in entries:
            entries[src] = []
        entries[src].append((x2, y2))
    return entries


def to_world(local_x, local_y, zone_pos):
    """Convert zone-local (2048×2048) coords to world map coords."""
    zx, zy, zw, zh = zone_pos
    wx = zx + (local_x / ZONE_MAP_SIZE) * zw
    wy = zy + (local_y / ZONE_MAP_SIZE) * zh
    return wx, wy


def fix_file(map_md):
    with open(map_md, "r", encoding="utf-8") as f:
        content = f.read()

    # Get zone positions
    positions = parse_zone_positions(content)
    if not positions:
        print(f"  {os.path.relpath(map_md, ROOT)}: no zones found, skipping")
        return False

    # Collect all TP lines with their coordinates
    tp_pattern = re.compile(
        r'(<line class="zonemap-tp[^"]*" '
        r'x1=")([\d.]+)(" y1=")([\d.]+)(" x2=")([\d.]+)(" y2=")([\d.]+)(" '
        r'stroke="[^"]*" stroke-width="[^"]*" stroke-dasharray="[^"]*" '
        r'vector-effect="non-scaling-stroke" '
        r'data-tps=")([^"]+)(" data-tpd=")([^"]+)(")'
    )
    
    # We need to process both casing and colored lines together since they share coordinates.
    # Strategy: collect all (src, dst) pairs, fix coordinates once, apply to both lines.
    
    # Group lines by (src, dst) to track ordering
    from collections import defaultdict
    lines_by_pair = defaultdict(list)
    
    for m in tp_pattern.finditer(content):
        src = m.group(10)
        dst = m.group(12)
        x1, y1 = float(m.group(2)), float(m.group(4))
        x2, y2 = float(m.group(6)), float(m.group(8))
        lines_by_pair[(src, dst)].append({
            'start': m.start(), 'end': m.end(),
            'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
            'raw': m.group(0),
            'match': m
        })
    
    # For each (src, dst) pair, get the correct coordinates from zone maps.
    # Lines come in pairs: (casing, colored) per TP point. Both lines in a
    # pair share the same coordinates.
    fixed_count = 0
    replacements = []  # (start, end, new_text)
    
    for (src, dst), lines in lines_by_pair.items():
        src_file = zone_slug_to_file(src)
        dst_file = zone_slug_to_file(dst)
        
        # Get source TP positions from src zone map
        src_tps = parse_zone_map_tps(src_file)
        src_positions = get_pos(positions, src)
        dst_positions = get_pos(positions, dst)
        
        if not src_positions or not dst_positions:
            continue
        
        # Get destination entry positions
        dst_entries = parse_zone_map_entries(dst_file)
        
        # Source coords: from src zone map's exit lines for this destination
        src_local_coords = src_tps.get(dst, [])
        # Destination coords: from dst zone map's entry lines from this source
        dst_local_coords = dst_entries.get(src, [])
        
        # Lines come in pairs: [casing_0, colored_0, casing_1, colored_1, ...]
        # The actual TP count is len(lines) / 2
        num_tps = len(lines) // 2
        
        for tp_idx in range(num_tps):
            # Both lines in this pair (casing + colored) get the same coords
            pair = lines[tp_idx * 2: tp_idx * 2 + 2]
            
            # Fix source (x1, y1)
            if tp_idx < len(src_local_coords):
                lx, ly = src_local_coords[tp_idx]
                new_x1, new_y1 = to_world(lx, ly, src_positions)
            else:
                new_x1, new_y1 = pair[0]['x1'], pair[0]['y1']
            
            # Fix destination (x2, y2)
            if tp_idx < len(dst_local_coords):
                lx, ly = dst_local_coords[tp_idx]
                new_x2, new_y2 = to_world(lx, ly, dst_positions)
            else:
                new_x2, new_y2 = pair[0]['x2'], pair[0]['y2']
            
            new_x1_s = f"{new_x1:.1f}"
            new_y1_s = f"{new_y1:.1f}"
            new_x2_s = f"{new_x2:.1f}"
            new_y2_s = f"{new_y2:.1f}"
            
            for line in pair:
                # Use raw text for the old coords (avoids float formatting issues)
                full = line['raw']
                # Extract the actual coordinate string from the raw match
                old_coord_str = re.search(r'x1="([^"]+)" y1="([^"]+)" x2="([^"]+)" y2="([^"]+)"', full)
                if not old_coord_str:
                    continue
                old_x1, old_y1, old_x2, old_y2 = old_coord_str.groups()
                
                if (old_x1, old_y1, old_x2, old_y2) != (new_x1_s, new_y1_s, new_x2_s, new_y2_s):
                    new_full = full.replace(
                        f'x1="{old_x1}" y1="{old_y1}" x2="{old_x2}" y2="{old_y2}"',
                        f'x1="{new_x1_s}" y1="{new_y1_s}" x2="{new_x2_s}" y2="{new_y2_s}"',
                        1
                    )
                    replacements.append((line['start'], line['end'], new_full))
                    fixed_count += 1
    
    # Apply replacements in reverse order (to preserve offsets)
    replacements.sort(key=lambda r: r[0], reverse=True)
    for start, end, new_text in replacements:
        content = content[:start] + new_text + content[end:]
    
    with open(map_md, "w", encoding="utf-8") as f:
        f.write(content)
    
    rel = os.path.relpath(map_md, ROOT)
    print(f"  {rel}: {fixed_count} TP lines corrected")
    return fixed_count > 0


if __name__ == "__main__":
    total = 0
    for map_file in find_map_files():
        if fix_file(map_file):
            total += 1
    print(f"\nDone. {total} files modified.")
