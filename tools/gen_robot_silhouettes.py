#!/usr/bin/env python3
"""Generate SVG robot silhouettes from OBJ files (front-view convex hull)."""
import sys, math, os

def parse_obj_verts(path):
    verts = []
    with open(path) as f:
        for line in f:
            if line.startswith('v '):
                parts = line.split()
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                verts.append((x, y))
    return verts

def convex_hull(points):
    """Andrew's monotone chain algorithm. Returns list of (x,y) tuples."""
    points = sorted(set(points))
    if len(points) <= 1:
        return points
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]

def normalize(hull, width=200, height=200):
    """Normalize hull to fit in width x height box, centered at 0."""
    xs = [p[0] for p in hull]
    ys = [p[1] for p in hull]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    spanx = maxx - minx or 1
    spany = maxy - miny or 1
    scale = min(width / spanx, height / spany) * 0.9
    cx = (minx + maxx) / 2
    cy = (miny + maxy) / 2
    return [( (x - cx) * scale, (y - cy) * scale ) for x, y in hull]

def hull_to_svg_path(hull, cx=0, cy=0):
    """Convert normalized hull to SVG path data (centered at cx,cy)."""
    if not hull:
        return ""
    parts = []
    for i, (x, y) in enumerate(hull):
        # SVG y is inverted (down = positive), game y is up
        sx = cx + x
        sy = cy - y
        if i == 0:
            parts.append(f"M {sx:.1f},{sy:.1f}")
        else:
            parts.append(f"L {sx:.1f},{sy:.1f}")
    parts.append("Z")
    return " ".join(parts)

def main():
    models_dir = sys.argv[1] if len(sys.argv) > 1 else "/mnt/spock/dev/game/openperpetuum/PerpetuumServer2/exported_models"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "/mnt/spock/dev/game/openperpetuum/wiki/static/robots-silhouettes.svg"

    robots = [
        ("scarab_v2", "Scarab"),
        ("waspish", "Waspish"),
        ("symbiont_v2", "Symbiont"),
        ("baphomet", "Baphomet"),
    ]

    # Generate silhouettes for each robot
    silhouettes = []
    for obj_name, label in robots:
        path = os.path.join(models_dir, f"{obj_name}.obj")
        if not os.path.exists(path):
            print(f"  SKIP {obj_name} (not found)")
            continue
        verts = parse_obj_verts(path)
        hull = convex_hull(verts)
        norm = normalize(hull, 160, 160)
        silhouettes.append((label, norm))
        print(f"  {label}: {len(verts)} verts -> {len(hull)} hull points")

    # Layout: 4 robots in a row across a wide card (800 x 300 viewBox)
    W, H = 800, 300
    n = len(silhouettes)
    spacing = W / n
    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" fill="none">')

    for i, (label, hull) in enumerate(silhouettes):
        cx = int(spacing * (i + 0.5))
        cy = H // 2 + 10
        d = hull_to_svg_path(hull, cx, cy)
        svg_parts.append(f'  <path d="{d}" fill="currentColor" opacity="0.08"/>')
        svg_parts.append(f'  <path d="{d}" stroke="currentColor" stroke-width="1" opacity="0.15" fill="none"/>')

    svg_parts.append('</svg>')

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        f.write('\n'.join(svg_parts))
    print(f"\nWrote {out_path} ({len(silhouettes)} robots)")

if __name__ == '__main__':
    main()
