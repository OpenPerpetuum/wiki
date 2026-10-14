#!/usr/bin/env python3
"""Post-build: add data-def attributes to item/ore/zone links in the built HTML.

The i18n runtime JS uses data-def="slug" to look up translated names.
This script scans the built HTML and adds the attribute to:
  - <a href="/content/items/<slug>/">  → data-def="<slug>"
  - <a href="/content/ores/<slug>/">   → data-def="<slug>"
  - <a href="/zones/zone-<slug>/">    → data-def="zone_<slug_underscored>"

It also sets data-page-def on <body> for the current page (so the JS can
translate the page title + h1).

This is idempotent: running it twice doesn't double-add attributes.

Usage:
  python3 tools/tag_defs.py <public-dir>
"""
import re
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

# Patterns: (regex, data-def value template)
# Only match links to specific data pages (not index/overview pages).
PATTERNS = [
    # /content/items/<slug>/  →  data-def="<slug>"
    (re.compile(r'href="(/content/items/([a-z0-9_\-]+)/)"'), r'\2'),
    # /content/ores/<slug>/   →  data-def="<slug>"
    (re.compile(r'href="(/content/ores/([a-z0-9_\-]+)/)"'), r'\2'),
    # /zones/zone-<slug>/     →  data-def="zone_<slug>" (hyphens → underscores)
    (re.compile(r'href="(/zones/(zone-[a-z0-9_\-]+)/)"'), None),  # special handling
]

# Known non-data zone pages (excluded from data-def)
ZONE_EXCLUDE = {
    'zone-map', 'zone-alpha', 'zone-beta', 'zone-gamma',
    'zone-protection', 'zone-generation', 'zone-index',
    'zone-training',
}


def zone_def(slug: str) -> str | None:
    """Return the data-def value for a zone URL slug (the slug itself)."""
    if slug in ZONE_EXCLUDE:
        return None
    return slug  # e.g. "zone-tm", "zone-asi-a-real"


def process_file(path: Path) -> int:
    """Add data-def attributes to one HTML file. Returns count of additions."""
    try:
        text = path.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError):
        return 0

    count = 0

    # 1) Item links: <a ... href="/content/items/slug/" ...>
    def fix_item(m):
        nonlocal count
        tag = m.group(0)
        if 'data-def=' in tag:
            return tag
        hm = re.search(r'href="/content/items/([a-z0-9_\-]+)/"', tag)
        if not hm:
            return tag
        slug = hm.group(1)
        tag = tag.replace(f'href="/content/items/{slug}/"',
                          f'href="/content/items/{slug}/" data-def="{slug}"', 1)
        count += 1
        return tag

    text = re.sub(r'<a [^>]*href="/content/items/[a-z0-9_\-]+/"[^>]*>', fix_item, text)

    # 2) Ore links: <a ... href="/content/ores/slug/" ...>
    def fix_ore(m):
        nonlocal count
        tag = m.group(0)
        if 'data-def=' in tag:
            return tag
        hm = re.search(r'href="/content/ores/([a-z0-9_\-]+)/"', tag)
        if not hm:
            return tag
        slug = hm.group(1)
        tag = tag.replace(f'href="/content/ores/{slug}/"',
                          f'href="/content/ores/{slug}/" data-def="{slug}"', 1)
        count += 1
        return tag

    text = re.sub(r'<a [^>]*href="/content/ores/[a-z0-9_\-]+/"[^>]*>', fix_ore, text)

    # 3) Zone links: <a ... href="/zones/zone-slug/" ...>
    def fix_zone(m):
        nonlocal count
        tag = m.group(0)
        if 'data-def=' in tag:
            return tag
        hm = re.search(r'href="/zones/(zone-[a-z0-9_\-]+)/"', tag)
        if not hm:
            return tag
        slug = hm.group(1)
        defval = zone_def(slug)
        if defval is None:
            return tag
        tag = tag.replace(f'href="/zones/{slug}/"',
                          f'href="/zones/{slug}/" data-def="{defval}"', 1)
        count += 1
        return tag

    text = re.sub(r'<a [^>]*href="/zones/zone-[a-z0-9_\-]+/"[^>]*>', fix_zone, text)

    # 4) Set data-page-def on <body> based on the file's own path
    #    The file is at public/<section>/<slug>/index.html
    #    For /content/items/alligior/index.html → data-page-def="alligior"
    #    For /content/ores/crude/index.html     → data-page-def="crude"
    #    For /zones/zone-tm/index.html          → data-page-def="zone_tm"
    parts = path.parts
    # Find the slug from the path
    page_def = None
    if len(parts) >= 3:
        # public/content/items/slug/index.html
        if len(parts) >= 4 and parts[-3] in ('items', 'ores'):
            page_def = parts[-2]
        elif parts[-3] == 'zones' and parts[-2].startswith('zone-'):
            zd = zone_def(parts[-2])
            if zd:
                page_def = zd  # the slug itself, e.g. "zone-tm"

    if page_def:
        # Add data-page-def to the <body> tag (before any existing data- attrs)
        if f'data-page-def=' not in text:
            text = text.replace('<body ', f'<body data-page-def="{page_def}" ', 1)
            count += 1

    if count:
        path.write_text(text, encoding='utf-8')

    return count


def main():
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} <public-dir>", file=sys.stderr)
        sys.exit(1)

    public = Path(sys.argv[1])
    if not public.is_dir():
        print(f"error: {public} is not a directory", file=sys.stderr)
        sys.exit(1)

    html_files = list(public.rglob("index.html"))
    print(f"tag_defs: processing {len(html_files)} HTML files...")

    total = 0
    with ProcessPoolExecutor() as pool:
        futures = {pool.submit(process_file, f): f for f in html_files}
        for fut in as_completed(futures):
            total += fut.result()

    print(f"tag_defs: added {total} data-def attributes")


if __name__ == "__main__":
    main()
