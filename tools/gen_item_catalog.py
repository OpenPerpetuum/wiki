#!/usr/bin/env python3
"""Generate item catalog index pages grouped by category.

Creates one page per top-level category under content/content/catalog/,
listing all items in that category with links, grouped by sub-category.

Also generates a "Components" page under content/content/ listing items
that are used as components in production recipes.

Usage: python3 tools/gen_item_catalog.py
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

REPO = Path(__file__).resolve().parent.parent
ITEMS_DIR = REPO / "content" / "content" / "items"
CATALOG_DIR = REPO / "content" / "content" / "catalog"
COMPONENTS_PAGE = REPO / "content" / "content" / "components.md"

# Category display names and ordering
CATEGORIES = [
    ("ammo", "Ammo", "Ammo catalog"),
    ("artifacts", "Artifacts", "Artifacts catalog"),
    ("decorations", "Decorations", "Decorations catalog"),
    ("materials", "Materials", "Materials catalog"),
    ("mission-items", "Mission items", "Mission items catalog"),
    ("modules", "Modules", "Modules catalog"),
    ("production", "Production items", "Production items catalog"),
    ("robot-parts", "Robot parts", "Robot parts catalog"),
    ("special-other", "Special & other", "Special & other catalog"),
]

# Map top-level description prefix to catalog slug
def desc_to_category(desc: str) -> str:
    """Map an item's description to its catalog category slug."""
    d = desc.lower()
    if d.startswith("ammo"):
        return "ammo"
    if d.startswith("artifact"):
        return "artifacts"
    if d.startswith("decoration"):
        return "decorations"
    if d.startswith("material"):
        return "materials"
    if d.startswith("mission"):
        return "mission-items"
    if d.startswith("module"):
        return "modules"
    if d.startswith("production"):
        return "production"
    if d.startswith("robot"):
        return "robot-parts"
    if d.startswith("special"):
        return "special-other"
    return "special-other"


def subcategory_of(desc: str, top_cat: str) -> str:
    """Extract the sub-category from the description."""
    # "Modules / Weapons, tier T1" -> "Weapons"
    # "Ammo / Mining" -> "Mining"
    # "Materials, tier T1" -> "Tier T1"
    # "Mission items / Landmarks" -> "Landmarks"
    # "Special & other / Fit capsules & programs, tier T2" -> "Fit capsules & programs"
    # "Decorations" -> ""
    # "Artifacts" -> ""
    
    # Remove the top-level prefix
    # Patterns: "Top / Sub, tier X" or "Top / Sub" or "Top, tier X" or just "Top"
    rest = desc
    # Try "Top / Sub" pattern
    if "/" in desc:
        parts = desc.split("/", 1)
        rest = parts[1].strip()
    else:
        # "Materials, tier T1" -> "tier T1"
        m = re.match(r'^[A-Za-z& ]+,\s*(.+)$', desc)
        if m:
            rest = m.group(1).strip()
        else:
            rest = ""
    
    # Remove tier suffix for grouping: "Weapons, tier T1" -> "Weapons"
    # But keep tier as a sub-group within
    tier_m = re.match(r'^(.*?),\s*tier (T\d)(?:\s*\(special\))?', rest)
    if tier_m:
        return tier_m.group(1).strip()
    
    # Remove "(special)" suffix
    rest = re.sub(r'\s*\(special\)', '', rest)
    
    if not rest or rest.lower() in (top_cat.lower(),):
        return ""
    
    return rest


def tier_of(desc: str) -> str:
    """Extract tier from description. 'Modules / Weapons, tier T1' -> 'T1'."""
    m = re.search(r'tier (T\d)', desc)
    if m:
        return m.group(1)
    if 'special' in desc.lower():
        return 'Special'
    return '—'


def slugify(s: str) -> str:
    """Convert a string to a URL-safe slug."""
    s = s.lower().replace("&", "and")
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')


def collect_items():
    """Read all item pages and return list of (slug, title, desc, category, subcategory)."""
    items = []
    for f in sorted(ITEMS_DIR.glob("*.md")):
        if f.name == "_index.md":
            continue
        content = f.read_text()
        # Extract title
        m = re.search(r'^title:\s*"?(.+?)"?\s*$', content, re.MULTILINE)
        title = m.group(1).strip().strip('"') if m else f.stem.replace("_", " ").title()
        # Extract description
        m = re.search(r'^description:\s*"?(.+?)"?\s*$', content, re.MULTILINE)
        desc = m.group(1).strip().strip('"') if m else ""
        # Extract definition ID for components page
        m = re.search(r'\| Definition \| `([^`]+)` \|', content)
        def_id = m.group(1) if m else ""
        
        cat = desc_to_category(desc)
        sub = subcategory_of(desc, cat)
        items.append({
            "slug": f.stem,
            "title": title,
            "desc": desc,
            "category": cat,
            "subcategory": sub,
            "def_id": def_id,
        })
    return items


def collect_components(items):
    """Find items that are used as components in other items' production."""
    component_slugs = set()
    for f in ITEMS_DIR.glob("*.md"):
        if f.name == "_index.md":
            continue
        content = f.read_text()
        if "production:generated" not in content:
            continue
        # Find component links: href="/content/items/{slug}/"
        links = re.findall(r'href="/content/items/([^/]+)/"', content)
        for slug in links:
            if slug != f.stem:  # exclude self-references
                component_slugs.add(slug)
    return component_slugs


def _render_cards(items: list, cat_title: str) -> list:
    """Render a list of items as mission-card HTML lines."""
    lines = []
    lines.append('<div class="mission-cards">')
    for item in items:
        url = f"/content/items/{item['slug'].replace('_', '-')}/"
        lines.append('<div class="mission-card">')
        lines.append('<div class="mission-card-head">')
        lines.append('<span class="icon-mask mission-card-icon" role="img" aria-label="item icon"></span>')
        lines.append(f'<div><div class="mission-card-title"><a href="{url}">{item["title"]}</a></div>')
        if item.get("subcategory") and item["subcategory"] != "(general)":
            lines.append(f'<div class="mission-card-sub">{item["desc"]}</div>')
        lines.append("</div>")
        lines.append("</div>")
        lines.append("</div>")
    lines.append("</div>")
    lines.append("")
    return lines


def generate_catalog_page(cat_slug: str, cat_title: str, cat_desc: str, items: list) -> str:
    """Generate a catalog index page for one category."""
    # Group by subcategory (by-type)
    subs = defaultdict(list)
    for item in items:
        sub = item["subcategory"] or "(general)"
        subs[sub].append(item)
    
    # Determine if this category supports dual-view (by-type + by-tier)
    dual_view = (cat_slug == "modules")
    
    lines = []
    lines.append("---")
    lines.append(f'title: "{cat_title}"')
    lines.append(f'description: "{cat_desc}"')
    lines.append("---")
    lines.append("")
    lines.append(f"<!-- Generated by tools/gen_item_catalog.py. Do not edit by hand; regenerate instead. -->")
    lines.append("")
    
    if dual_view:
        # Heading with toggle
        lines.append(f'<div class="catalog-dual-header">')
        lines.append(f'<h1>{cat_title}</h1>')
        lines.append(f'<span class="catalog-count">{len(items)} items</span>')
        lines.append(f'<div class="catalog-toggle">')
        lines.append(f'<button class="catalog-toggle-btn active" data-view="type">by-type</button>')
        lines.append(f'<button class="catalog-toggle-btn" data-view="tier">by-tier</button>')
        lines.append(f'</div>')
        lines.append(f'</div>')
        lines.append("")
    else:
        lines.append(f"# {cat_title}")
        lines.append("")
        lines.append(f"{len(items)} items.")
        lines.append("")
    
    if dual_view:
        # --- BY-TYPE VIEW ---
        lines.append('<div class="catalog-view" data-view="type">')
        if len(subs) > 1:
            lines.append('<div class="mission-index">')
            toc_parts = []
            for sub in sorted(subs.keys()):
                slug = slugify(sub)
                toc_parts.append(f'<a href="#{slug}"><span class="mission-type-chip">{sub} ({len(subs[sub])})</span></a>')
            lines.append("&ensp; ".join(toc_parts))
            lines.append("</div>")
            lines.append("")
        for sub in sorted(subs.keys()):
            sub_items = subs[sub]
            sub_title = sub if sub != "(general)" else cat_title
            if len(subs) > 1 or sub != "(general)":
                lines.append(f"## {sub_title} ({len(sub_items)})")
                lines.append("")
            lines.extend(_render_cards(sub_items, cat_title))
        lines.append('</div>')
        lines.append("")
        
        # --- BY-TIER VIEW ---
        tiers = defaultdict(list)
        for item in items:
            t = tier_of(item["desc"])
            tiers[t].append(item)
        # Sort tiers: T1, T2, T3, T4, T5, Special, —
        tier_order = {'T1': 1, 'T2': 2, 'T3': 3, 'T4': 4, 'T5': 5, 'Special': 6, '—': 99}
        lines.append('<div class="catalog-view" data-view="tier" style="display:none">')
        lines.append('<div class="mission-index">')
        toc_parts = []
        for t in sorted(tiers.keys(), key=lambda x: tier_order.get(x, 50)):
            slug = slugify(t)
            toc_parts.append(f'<a href="#tier-{slug}"><span class="mission-type-chip">{t} ({len(tiers[t])})</span></a>')
        lines.append("&ensp; ".join(toc_parts))
        lines.append("</div>")
        lines.append("")
        for t in sorted(tiers.keys(), key=lambda x: tier_order.get(x, 50)):
            t_items = tiers[t]
            lines.append(f'<h2 id="tier-{slugify(t)}">{t} ({len(t_items)})</h2>')
            lines.append("")
            lines.extend(_render_cards(t_items, cat_title))
        lines.append('</div>')
        lines.append("")
        
        # Toggle JS (inline, small)
        lines.append('<script>')
        lines.append('(function(){var w=document.currentScript.parentElement;')
        lines.append('var btns=w.querySelectorAll(".catalog-toggle-btn");')
        lines.append('var views=w.querySelectorAll(".catalog-view");')
        lines.append('btns.forEach(function(b){b.addEventListener("click",function(){')
        lines.append('btns.forEach(function(x){x.classList.remove("active")});')
        lines.append('b.classList.add("active");')
        lines.append('var v=b.getAttribute("data-view");')
        lines.append('views.forEach(function(v2){v2.style.display=v2.getAttribute("data-view")==v?"":"none"});')
        lines.append('});});})();')
        lines.append('</script>')
    else:
        # Simple single-view page (non-modules)
        if len(subs) > 1:
            lines.append('<div class="mission-index">')
            toc_parts = []
            for sub in sorted(subs.keys()):
                slug = slugify(sub)
                toc_parts.append(f'<a href="#{slug}"><span class="mission-type-chip">{sub} ({len(subs[sub])})</span></a>')
            lines.append("&ensp; ".join(toc_parts))
            lines.append("</div>")
            lines.append("")
        for sub in sorted(subs.keys()):
            sub_items = subs[sub]
            sub_title = sub if sub != "(general)" else cat_title
            if len(subs) > 1 or sub != "(general)":
                lines.append(f"## {sub_title} ({len(sub_items)})")
                lines.append("")
            lines.extend(_render_cards(sub_items, cat_title))
    
    lines.append("")
    return "\n".join(lines)


def generate_components_page(items: list, component_slugs: set) -> str:
    """Generate the components index page."""
    # Filter to only items that exist in our catalog.
    # Links in pages may use hyphens while file stems use underscores, so
    # build a lookup that handles both forms.
    item_by_slug = {}
    for item in items:
        item_by_slug[item["slug"]] = item
        item_by_slug[item["slug"].replace("_", "-")] = item
    comp_items = [item_by_slug[s] for s in sorted(component_slugs) if s in item_by_slug]
    # Deduplicate (same item might match via both slug forms)
    seen = set()
    deduped = []
    for item in comp_items:
        if item["slug"] not in seen:
            seen.add(item["slug"])
            deduped.append(item)
    comp_items = deduped
    
    # Group by category
    by_cat = defaultdict(list)
    for item in comp_items:
        by_cat[item["category"]].append(item)
    
    lines = []
    lines.append("---")
    lines.append('title: "Components"')
    lines.append('description: "Items used as components in production recipes."')
    lines.append("---")
    lines.append("")
    lines.append("<!-- Generated by tools/gen_item_catalog.py. Do not edit by hand; regenerate instead. -->")
    lines.append("")
    lines.append("# Components")
    lines.append("")
    lines.append(f"{len(comp_items)} items are used as components in [production recipes](/content/recipes/).")
    lines.append("")
    
    # TOC
    if len(by_cat) > 1:
        lines.append('<div class="mission-index">')
        toc_parts = []
        for cat_slug, cat_title, _ in CATEGORIES:
            if cat_slug in by_cat:
                toc_parts.append(f'<a href="#{cat_slug}"><span class="mission-type-chip">{cat_title} ({len(by_cat[cat_slug])})</span></a>')
        lines.append("&ensp; ".join(toc_parts))
        lines.append("</div>")
        lines.append("")
    
    for cat_slug, cat_title, _ in CATEGORIES:
        if cat_slug not in by_cat:
            continue
        cat_items = by_cat[cat_slug]
        lines.append(f"## {cat_title} ({len(cat_items)})")
        lines.append("")
        lines.append('<div class="mission-cards">')
        for item in cat_items:
            url = f"/content/items/{item['slug'].replace('_', '-')}/"
            lines.append('<div class="mission-card">')
            lines.append('<div class="mission-card-head">')
            lines.append('<span class="icon-mask mission-card-icon" role="img" aria-label="item icon"></span>')
            lines.append(f'<div><div class="mission-card-title"><a href="{url}">{item["title"]}</a></div>')
            lines.append(f'<div class="mission-card-sub">{item["desc"]}</div>')
            lines.append("</div>")
            lines.append("</div>")
            lines.append("</div>")
        lines.append("</div>")
        lines.append("")
    
    lines.append("")
    return "\n".join(lines)


def main():
    print("gen_item_catalog: reading item pages...")
    items = collect_items()
    print(f"  {len(items)} items found")
    
    # Group by category
    by_cat = defaultdict(list)
    for item in items:
        by_cat[item["category"]].append(item)
    
    for cat_slug, cat_title, _ in CATEGORIES:
        count = len(by_cat.get(cat_slug, []))
        print(f"  {cat_slug}: {count} items")
    
    # Generate catalog pages
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Write _index.md for the catalog section
    index_lines = ["---", 'title: "Item catalog"', 'description: "Browse all items by category."', "---", ""]
    index_lines.append("# Item catalog")
    index_lines.append("")
    index_lines.append("Browse all items grouped by category.")
    index_lines.append("")
    index_lines.append('<div class="mission-index">')
    toc_parts = []
    for cat_slug, cat_title, _ in CATEGORIES:
        count = len(by_cat.get(cat_slug, []))
        if count > 0:
            toc_parts.append(f'<a href="/content/catalog/{cat_slug}/"><span class="mission-type-chip">{cat_title} ({count})</span></a>')
    index_lines.append("&ensp; ".join(toc_parts))
    index_lines.append("</div>")
    index_lines.append("")
    (CATALOG_DIR / "_index.md").write_text("\n".join(index_lines))
    print(f"  wrote {CATALOG_DIR / '_index.md'}")
    
    for cat_slug, cat_title, cat_desc in CATEGORIES:
        cat_items = by_cat.get(cat_slug, [])
        if not cat_items:
            continue
        page = generate_catalog_page(cat_slug, cat_title, cat_desc, cat_items)
        out = CATALOG_DIR / f"{cat_slug}.md"
        out.write_text(page)
        print(f"  wrote {out.relative_to(REPO)} ({len(cat_items)} items)")
    
    # Generate components page
    print("  collecting component relationships...")
    component_slugs = collect_components(items)
    print(f"  {len(component_slugs)} unique components found")
    page = generate_components_page(items, component_slugs)
    COMPONENTS_PAGE.write_text(page)
    print(f"  wrote {COMPONENTS_PAGE.relative_to(REPO)} ({len(component_slugs)} components)")
    
    print("Done.")


if __name__ == "__main__":
    main()
