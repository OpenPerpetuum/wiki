#!/usr/bin/env python3
"""transform_world_map.py — rework the world map SVG to use coastline clipping
(the same technique as the zone maps) and zone-map-style TP lines.

Transforms:
1. Each zone's <image> elements are wrapped in a <g clip-path="..."> using the
   coastline path from that zone's thumb.svg. A dark background path is added
   behind the clipped image so the island shape is visible against the sea.
2. TP lines are replaced with the zone-map style: a dark casing line + a
   colored line, both with stroke-dasharray="5 4" and vector-effect:
   non-scaling-stroke. The gradient <defs> are removed.

Usage: python3 tools/transform_world_map.py
"""
import re
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
ZONEMAPS = os.path.join(ROOT, "static", "zonemaps")


def load_coastline(zone_slug):
    """Load the coastline path, viewBox size, and stroke color from a zone's thumb.svg."""
    thumb_path = os.path.join(ZONEMAPS, zone_slug, "thumb.svg")
    if not os.path.isfile(thumb_path):
        return None, None, None
    with open(thumb_path, "r", encoding="utf-8") as f:
        data = f.read()
    m_vb = re.search(r'viewBox="0 0 (\d+) (\d+)"', data)
    # The first <path> is the coastline (filled island shape)
    m_path = re.search(r'<path[^>]*stroke="([^"]+)"[^>]*d="([^"]+)"', data)
    if not m_path:
        m_path = re.search(r'<path[^>]*d="([^"]+)"[^>]*stroke="([^"]+)"', data)
    if m_vb and m_path:
        size = int(m_vb.group(1))
        # Handle both attribute orders
        if 'stroke' in m_path.group(0).split('d=')[0]:
            stroke = m_path.group(1)
            d = m_path.group(2)
        else:
            d = m_path.group(1)
            stroke = m_path.group(2)
        return d, size, stroke
    return None, None, None


def find_map_files():
    """Find all zones/map.md files across all languages."""
    files = []
    for dirpath, _, filenames in os.walk(CONTENT):
        if "map.md" in filenames and dirpath.endswith("/zones"):
            files.append(os.path.join(dirpath, "map.md"))
    return sorted(files)


def transform_file(map_md, clip_defs):
    """Transform a single map.md file. Returns the transformed content."""
    with open(map_md, "r", encoding="utf-8") as f:
        content = f.read()

    # --- 1. Transform zone nodes: add clipPath + background + clip group ---
    clip_defs = []  # clipPath definitions to add to <defs>
    
    def replace_zone_images(match):
        full = match.group(0)
        # Extract the zone slug from the first image href
        m_href = re.search(r'href="/zonemaps/([^/]+)/thumb\.svg"', full)
        if not m_href:
            return full
        slug = m_href.group(1)
        
        # Extract position and size from the first image
        m_x = re.search(r'x="([\d.]+)"', full)
        m_y = re.search(r'y="([\d.]+)"', full)
        m_w = re.search(r'width="([\d.]+)"', full)
        m_h = re.search(r'height="([\d.]+)"', full)
        if not all([m_x, m_y, m_w, m_h]):
            return full
        x, y = float(m_x.group(1)), float(m_y.group(1))
        w, h = float(m_w.group(1)), float(m_h.group(1))
        
        # Load the coastline
        coast_d, coast_size, coast_stroke = load_coastline(slug)
        if not coast_d:
            return full  # no coastline available, keep as-is
        if not coast_stroke:
            coast_stroke = "#2a364b"
        
        # Calculate the transform: scale from coast_size to w, translate to (x, y)
        sx = w / coast_size
        sy = h / coast_size
        transform = f"translate({x}, {y}) scale({sx:.6f}, {sy:.6f})"
        clip_id = f"wm-clip-{slug}"
        
        # Add the clipPath definition
        clip_defs.append(
            f'    <clipPath id="{clip_id}"><path transform="{transform}" d="{coast_d}"/></clipPath>'
        )
        
        # Build the replacement: background path + clipped group
        # Replace .png references with .svg (vector renders scale cleanly)
        full = re.sub(r'href="(/zonemaps/[^"]+?)\.png"', r'href="\1.svg"', full)
        images = re.findall(r'<image class="wm-(?:base|height|color)"[^>]*?/>', full)
        
        result_parts = []
        # Dark background (island fill)
        result_parts.append(f'<path transform="{transform}" d="{coast_d}" fill="#10151f"/>')
        # Clipped group containing the images
        result_parts.append(f'<g clip-path="url(#{clip_id})">')
        for img in images:
            result_parts.append(img)
        result_parts.append('</g>')
        # Coastline stroke on top (visible in all display modes, colored by protection level)
        result_parts.append(f'<path transform="{transform}" d="{coast_d}" fill="none" stroke="{coast_stroke}" stroke-width="0.3" vector-effect="non-scaling-stroke" class="wm-coastline"/>')
        
        return "".join(result_parts)
    
    # Match groups of consecutive wm-* images (base + optional height + color)
    # The images are self-closing: <image ... />
    # They are always followed by a <circle or <text or </g>
    pattern = re.compile(
        r'<image class="wm-base"[^>]*?/>'
        r'(?:<image class="wm-(?:height|color)"[^>]*?/>)*'
    )
    content = pattern.sub(replace_zone_images, content)
    
    # --- 2. Transform TP lines to zone-map style ---
    
    # Extract source color from gradients (stop offset=0 is the source color)
    grad_colors = {}
    for m in re.finditer(r'<linearGradient id="(tpg\d+)"[^>]*>\s*<stop offset="0" stop-color="([^"]+)"', content):
        grad_colors[m.group(1)] = m.group(2)
    
    def replace_tp_line(match):
        line = match.group(0)
        m_grad = re.search(r'stroke="url\(#(tpg\d+)\)"', line)
        m_x1 = re.search(r'x1="([^"]+)"', line)
        m_y1 = re.search(r'y1="([^"]+)"', line)
        m_x2 = re.search(r'x2="([^"]+)"', line)
        m_y2 = re.search(r'y2="([^"]+)"', line)
        m_tps = re.search(r'data-tps="([^"]*)"', line)
        m_tpd = re.search(r'data-tpd="([^"]*)"', line)
        m_title = re.search(r'<title>([^<]*)</title>', line)
        
        if not all([m_grad, m_x1, m_y1, m_x2, m_y2]):
            return line
        
        grad_id = m_grad.group(1)
        color = grad_colors.get(grad_id, "#c8d2e0")
        x1, y1 = m_x1.group(1), m_y1.group(1)
        x2, y2 = m_x2.group(1), m_y2.group(1)
        tps = m_tps.group(1) if m_tps else ""
        tpd = m_tpd.group(1) if m_tpd else ""
        title = m_title.group(1) if m_title else ""
        
        # Zone-map style: casing + colored line
        data_attrs = f' data-tps="{tps}" data-tpd="{tpd}"'
        title_tag = f"<title>{title}</title>" if title else ""
        
        casing = (
            f'<line class="zonemap-tp zm-tp-casing" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="#0a0f18" stroke-width="0.6" stroke-dasharray="5 4" '
            f'vector-effect="non-scaling-stroke"{data_attrs}/>'
        )
        colored = (
            f'<line class="zonemap-tp" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="0.3" stroke-dasharray="5 4" '
            f'vector-effect="non-scaling-stroke"{data_attrs}>{title_tag}</line>'
        )
        return casing + "\n  " + colored
    
    # Match TP lines (self-closing or with <title> child)
    tp_pattern = re.compile(
        r'<line\s[^>]*class="zonemap-tp"[^>]*>(?:<title>[^<]*</title>)?</line>'
    )
    content = tp_pattern.sub(replace_tp_line, content)
    
    # --- 3. Remove the gradient definitions (no longer needed) ---
    content = re.sub(r'\s*<linearGradient id="tpg\d+"[^>]*>.*?</linearGradient>', '', content, flags=re.DOTALL)
    
    # --- 4. Insert clipPath definitions into <defs> ---
    if clip_defs:
        defs_content = "\n".join(clip_defs)
        content = content.replace("<defs>\n", f"<defs>\n{defs_content}\n", 1)
    
    with open(map_md, "w", encoding="utf-8") as f:
        f.write(content)

    rel = os.path.relpath(map_md, ROOT)
    print(f"  {rel}: {len(clip_defs)} zones")


if __name__ == "__main__":
    total_zones = 0
    for map_file in find_map_files():
        clip_defs = []
        transform_file(map_file, clip_defs)
        total_zones = len(clip_defs)
    print(f"\nDone. {total_zones} zone nodes per file, {len(find_map_files())} files.")
