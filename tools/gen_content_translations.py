#!/usr/bin/env python3
"""Generate localized content pages in content/<lang>/content/ for all 13 supported languages.

Generates:
- content/<lang>/content/_index.md
- content/<lang>/content/ores.md + content/<lang>/content/ores/*.md (19 files)
- content/<lang>/content/plants.md
- content/<lang>/content/missions.md
- content/<lang>/content/deployables.md + content/<lang>/content/deployables/*.md (220 files)
- content/<lang>/content/robots.md + content/<lang>/content/robots/*.md (117 files)
- content/<lang>/content/recipes.md
- content/<lang>/content/techtree/_index.md + content/<lang>/content/techtree/groups/*.md (7 files)
- content/<lang>/content/extensions.md
- content/<lang>/content/stat-reference.md
- content/<lang>/content/shop.md + content/<lang>/content/shop/*.md (11 files)

All translatable strings come from translations/<lang>.json (single source of
truth, see tools/i18n_common.py); missing keys fall back to English.

All internal markdown/HTML links are rewritten to their /{lang}/ routes,
except /content/items/ and /zones/ which remain global.
"""
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from i18n_common import t, rewrite_links

LANGUAGES = [
    "cs", "de", "es", "fr", "it", "ja", "ko",
    "nl", "pl", "pt", "ru", "zh-CN", "zh-TW"
]


def process_robot_file(content, lang):
    """Translate an individual robot page."""
    c = rewrite_links(content, lang)

    # Translate card stats
    for stat in ["combat", "speed", "armor", "storage", "cost"]:
        stat_tr = t(lang, "labels", stat)
        c = re.sub(rf'<span>{stat.capitalize()}</span>', f'<span>{stat_tr}</span>', c)

    # Translate properties table
    for prop in ["class", "size", "mass", "health", "purchasable"]:
        prop_tr = t(lang, "labels", prop)
        c = re.sub(rf'<td>{prop.capitalize()}</td>', f'<td>{prop_tr}</td>', c)

    yes_tr = t(lang, "labels", "yes")
    no_tr = t(lang, "labels", "no")
    c = re.sub(r'<td>Yes</td>', f'<td>{yes_tr}</td>', c)
    c = re.sub(r'<td>No</td>', f'<td>{no_tr}</td>', c)

    # Translate section headers & production
    c = c.replace("## Variants", f"## {t(lang, 'robots', 'variants')}")
    c = c.replace("| Variant | Link |", f"| {t(lang, 'robots', 'variant')} | {t(lang, 'robots', 'link')} |")
    c = c.replace("## Production", f"## {t(lang, 'robots', 'production')}")
    c = c.replace("Components required to build this robot:", t(lang, "robots", "components_required"))
    c = c.replace("| Component | Amount |", f"| {t(lang, 'robots', 'component')} | {t(lang, 'labels', 'amount')} |")

    c = c.replace("## NPC Vendor", f"## {t(lang, 'robots', 'npc_vendor')}")
    c = c.replace("Available from the NPC vendor:", t(lang, "robots", "available_from_npc"))
    c = c.replace("**Price:**", f"**{t(lang, 'robots', 'price')}**")

    # Frontmatter description: "{Name} — robot stats, production and availability."
    m = re.search(r'title:\s*"([^"]+)"', c)
    if m:
        bot_name = m.group(1)
        desc_tr = t(lang, "robots", "frontmatter_desc").replace("{Robot}", bot_name).replace("{name}", bot_name)
        c = re.sub(r'description:\s*"[^"]*"', f'description: "{desc_tr}"', c)

    return c


# Full intro paragraph of an individual ore page (matched before the generic
# extraction-type replacements, which only handle the table cell).
ORE_INTRO_RE = re.compile(
    r'\*\*([^*]+)\*\* is a (liquid \(pumped continuously\)|solid \(drilled tile by tile\)) ore\. '
    r'Each extraction yields \*\*([^*]+)\*\* units, and the zone holds it in finite '
    r'\*\*deposits \(nodes\)\*\* — when a node is mined below its threshold it is removed '
    r'and the zone regenerates nodes up to its configured maximum\. '
    r'How the node-generation columns below are used by the server is in \[Ore fields\]\(([^)]+)\)\.'
)


def process_ore_file(content, lang):
    """Translate an individual ore page."""
    c = rewrite_links(content, lang)

    # Frontmatter description: "{Name}: extraction yield, the zones it spawns in, and what is made from it."
    m = re.search(r'title:\s*"([^"]+)"', c)
    if m:
        ore_name = m.group(1)
        fm = t(lang, "ores", "frontmatter_desc").replace("{name}", ore_name)
        c = re.sub(r'description:\s*"[^"]*"', f'description: "{fm}"', c)

    # Intro paragraph (template with name/type/amount; the Ore-fields link is rebuilt
    # with its already-rewritten href)
    def _repl_intro(m):
        name, etype, amount, href = m.groups()
        type_tr = t(lang, "ores", "liquid") if etype.startswith("liquid") else t(lang, "ores", "solid")
        out = (t(lang, "ores", "intro")
               .replace("{name}", name)
               .replace("{type}", type_tr)
               .replace("{amount}", amount))
        out = out.replace("[Ore fields](/formats/ore-fields/)",
                          f"[{t(lang, 'ores', 'ore_fields_link')}]({href})")
        return out

    c = ORE_INTRO_RE.sub(_repl_intro, c)

    c = c.replace("## Extraction", f"## {t(lang, 'ores', 'extraction')}")
    c = c.replace("| Property | Value |", f"| {t(lang, 'labels', 'property')} | {t(lang, 'labels', 'value')} |")
    c = c.replace("| Amount / extraction |", f"| {t(lang, 'ores', 'amount_extraction')} |")
    c = c.replace("| Extraction type |", f"| {t(lang, 'ores', 'extraction_type')} |")
    c = c.replace("| Enabler effect |", f"| {t(lang, 'ores', 'enabler_effect')} |")
    c = c.replace("| Geo-scan document |", f"| {t(lang, 'ores', 'geo_scan_document')} |")

    c = c.replace("liquid (pumped continuously)", t(lang, "ores", "liquid"))
    c = c.replace("solid (drilled tile by tile)", t(lang, "ores", "solid"))
    c = c.replace("not required", t(lang, "ores", "not_required"))
    c = c.replace("| required |", f"| {t(lang, 'ores', 'required')} |")

    c = c.replace("## Where it spawns", f"## {t(lang, 'ores', 'where_it_spawns')}")
    c = c.replace(
        "Zones that regenerate this ore, with their node configuration. Zones without an entry do not hold this ore.",
        t(lang, "ores", "spawns_intro")
    )
    c = c.replace(
        "This ore has no zone node configuration — it is not regenerated in any zone (it exists as a material for production and missions).",
        t(lang, "ores", "no_spawn")
    )
    c = c.replace(
        "| Zone | Max nodes | Max tiles / node | Total amount / node | Min threshold |",
        f"| {t(lang, 'ores', 'col_zone')} | {t(lang, 'ores', 'col_max_nodes')} | "
        f"{t(lang, 'ores', 'col_max_tiles_per_node')} | {t(lang, 'ores', 'col_total_per_node')} | "
        f"{t(lang, 'ores', 'col_min_threshold')} |"
    )

    c = c.replace("## Made from it", f"## {t(lang, 'ores', 'made_from_it')}")
    c = c.replace(
        "Items that take this ore as a recipe component (amount per single production). Full component lists are on each item's page.",
        t(lang, "ores", "made_from_p")
    )

    def _repl_made_header(m):
        ore = m.group(1)
        return (f"| {t(lang, 'shop', 'item')} | "
                f"{t(lang, 'ores', 'amount_of').replace('{name}', ore)} | "
                f"{t(lang, 'missions', 'research_level')} |")

    c = re.sub(r'\| Item \| Amount of ([^|]+) \| Research level \|', _repl_made_header, c)
    c = c.replace("| Item | Amount |", f"| {t(lang, 'shop', 'item')} | {t(lang, 'labels', 'amount')} |")

    return c


DEPLOYABLE_CATS = {
    "Power base stations": "cat_pbs",
    "Mines & bombs": "cat_mines",
    "Mobile fields": "cat_mobile_fields",
    "Mobile teleports": "cat_mobile_tps",
    "Arena teleports": "cat_arena_tps",
    "Miscellaneous": "cat_misc",
    "Plant seeds": "cat_seeds",
    "NPC eggs": "cat_eggs",
    "Gates": "cat_gates",
    "Containers": "cat_containers",
    "Wall repairers": "cat_wall",
}


def process_deployable_file(content, lang):
    """Translate an individual deployable page."""
    c = rewrite_links(content, lang)

    # Frontmatter description: "{Category}: {Name}"
    m = re.search(r'description:\s*"([^":]+): ([^"]+)"', c)
    if m:
        cat, name = m.group(1), m.group(2)
        key = DEPLOYABLE_CATS.get(cat)
        cat_tr = t(lang, "deployables", key) if key else cat
        desc_tr = t(lang, "deployables", "desc").replace("{category}", cat_tr).replace("{name}", name)
        c = re.sub(r'description:\s*"[^"]*"', f'description: "{desc_tr}"', c)

    for field in ["definition", "category", "tier", "health", "volume", "mass"]:
        f_tr = t(lang, "labels", field)
        c = re.sub(rf'\|\s*{field.capitalize()}\s*\|', f'| {f_tr} |', c)

    c = c.replace("## Stats", f"## {t(lang, 'labels', 'stats')}")
    c = c.replace("| Field | Value |", f"| {t(lang, 'labels', 'field')} | {t(lang, 'labels', 'value')} |")

    all_dep = t(lang, "labels", "all_deployables")
    dep_f = t(lang, "labels", "deployable_fields")
    c = re.sub(r'\[All deployables\]\([^)]+\)', f'[{all_dep}](/{lang}/content/deployables/)', c)
    c = re.sub(r'\[Deployable fields\]\([^)]+\)', f'[{dep_f}](/{lang}/formats/deployable-fields/)', c)

    return c


def process_shop_file(content, lang):
    """Translate an individual shop category page."""
    c = rewrite_links(content, lang)

    # Frontmatter title/description (the category is the H1 text; category names are
    # in-game vendor taxonomy and stay in English)
    m = re.search(r'^#\s*(.+)$', c, flags=re.MULTILINE)
    if m:
        category = m.group(1).strip()
        c = re.sub(r'title:\s*"[^"]*"',
                   f'title: "{t(lang, "shop", "title").replace("{category}", category)}"', c)
        c = re.sub(r'description:\s*"[^"]*"',
                   f'description: "{t(lang, "shop", "desc").replace("{category}", category)}"', c)

    # Table header (any currency-column variant): translate the common cells, keep the
    # currency names (in-game terms)
    def _repl_header(m):
        line = m.group(0)
        line = line.replace("| Item |", f"| {t(lang, 'shop', 'item')} |")
        line = line.replace("| Qty |", f"| {t(lang, 'shop', 'qty')} |")
        line = line.replace("| Vendors |", f"| {t(lang, 'shop', 'vendors')} |")
        return line

    c = re.sub(r'^\| Item \|.*\|$', _repl_header, c, flags=re.MULTILINE)

    # Currencies legend (category-page variant)
    c = c.replace(
        "**Currencies** — **TM Coin / ICS Coin / ASI Coin**: the per-galaxy shop currency; **Credits**: the common currency; **UniCoin**: a premium currency. Each row shows the best terms across all vendors that sell the item. **Qty ∞** means the vendor has no stock limit.",
        t(lang, "shop", "currency_legend")
    )

    # Vendor locations: the place names are in-game terms, the zone/outpost words translate
    c = c.replace("TM zone", t(lang, "shop", "vendor_tm"))
    c = c.replace("ICS zone", t(lang, "shop", "vendor_ics"))
    c = c.replace("ASI zone", t(lang, "shop", "vendor_asi"))
    c = c.replace("Daoden outpost", t(lang, "shop", "vendor_daoden"))
    c = c.replace("Attalica outpost", t(lang, "shop", "vendor_attalica"))

    # Breadcrumb
    item_shop = t(lang, "labels", "item_shop")
    c = re.sub(r'\[Item shop\]\([^)]+\)', f'[{item_shop}](/{lang}/content/shop/)', c)

    return c


TECHTREE_GROUP_INTROS = [
    ("The first set of standard (non-faction) modules available to every player.", "intros_common1"),
    ("The second set of standard modules, including the named energy-transfer lines.", "intros_common2"),
    ("Industrial research: reactor boosters and the modules that keep production lines moving.", "intros_indy"),
    ("Research for the Nuimqol rebel faction: its named weapons and the modules that fight alongside them.", "intros_nuimqol"),
    ("Power base station capsules and construction modules — the buildings of open-world corporate play.", "intros_pbs"),
    ("Research for the Pelistal domain faction: its named weapons and the modules that fight alongside them.", "intros_pelistal"),
    ("Research for the Thelodica Clan faction: its named weapons and the modules that fight alongside them.", "intros_thelodica"),
]


def process_techtree_group_file(content, lang):
    """Translate a techtree group page."""
    c = rewrite_links(content, lang)

    # Frontmatter title/description (the category is the H1 text; category names are
    # in-game taxonomy and stay in English)
    m = re.search(r'^#\s*(.+)$', c, flags=re.MULTILINE)
    if m:
        category = m.group(1).strip()
        c = re.sub(r'title:\s*"[^"]*"',
                   f'title: "{t(lang, "techtree", "cat_title").replace("{category}", category)}"', c)
        mm = re.search(r'description:\s*"[^\"]*?(\d+) nodes\."', c)
        count = mm.group(1) if mm else "?"
        c = re.sub(r'description:\s*"[^"]*"',
                   f'description: "{t(lang, "techtree", "cat_desc").replace("{category}", category).replace("{count}", count)}"', c)

    # Category intro paragraph (one per group)
    for intro, key in TECHTREE_GROUP_INTROS:
        c = c.replace(intro, t(lang, "techtree", key))

    # "{Tech tree} → {Category}. The category is split into its **research lines** — ..."
    def _repl_intro_line(m):
        href, category = m.group(1), m.group(2)
        link = f"[{t(lang, 'labels', 'tech_tree')}]({href})"
        return (t(lang, "techtree", "cat_intro_line")
                .replace("{techtree_link}", link)
                .replace("{category}", category))

    c = re.sub(
        r'\[Tech tree\]\(([^)]+)\) → (.+?)\. The category is split into its \*\*research lines\*\* — '
        r"one per top-level item \(the chips above jump to each line's graph\)\. "
        r'Every node in a graph links to its detail page \(prerequisites, what it unlocks next, point prices\)\.',
        _repl_intro_line, c
    )

    tt = t(lang, "labels", "tech_tree")
    c = re.sub(r'\[Tech tree\]\([^)]+\)', f'[{tt}](/{lang}/content/techtree/)', c)

    # Line descriptions: "**16 nodes** — everything that descends from [X](url)."
    def repl_nodes(m):
        count, link = m.group(1), m.group(2)
        return t(lang, "techtree", "nodes_desc").replace("{count}", count).replace("{link}", link)

    c = re.sub(r'\*\*(\d+)\s+nodes\*\*\s*—\s*everything that descends from (\[[^\]]+\]\([^)]+\))\.', repl_nodes, c)

    # Singular line description: "**1 node** — everything that descends from [X](url)."
    def repl_node_sing(m):
        count, link = m.group(1), m.group(2)
        return t(lang, "techtree", "node_desc").replace("{count}", count).replace("{link}", link)

    c = re.sub(r'\*\*(\d+)\s+node\*\*\s*—\s*everything that descends from (\[[^\]]+\]\([^)]+\))\.', repl_node_sing, c)

    return c


def process_techtree_node_file(content, lang):
    """Translate an individual tech tree node page."""
    c = rewrite_links(content, lang)

    # Frontmatter title: "{Name} — tech tree node"
    m = re.search(r'title:\s*"(.+?) — tech tree node"', c)
    if m:
        node_name = m.group(1)
        new_title = t(lang, "techtree", "node_title").replace("{name}", node_name)
        # lambda: avoid re.sub backslash-unescape of the replacement text
        c = re.sub(r'title:\s*"[^"]*"', lambda m: f'title: "{new_title}"', c)

    # Frontmatter description: "Research node that unlocks {Name} ({Category} category)."
    m2 = re.search(r'description:\s*"Research node that unlocks (.+?) \((.+?) category\)\."', c)
    if m2:
        name, cat = m2.group(1), m2.group(2)
        new_desc = t(lang, "techtree", "node_desc_fm").replace("{name}", name).replace("{category}", cat)
        c = re.sub(r'description:\s*"[^"]*"', lambda m: f'description: "{new_desc}"', c)

    # H1: "# {Name} (research node)"
    def _repl_h1(m):
        return "# " + t(lang, "techtree", "node_h1").replace("{name}", m.group(1))

    c = re.sub(r'^#\s*(.+?) \(research node\)$', _repl_h1, c, flags=re.MULTILINE)

    # Intro: "This node of the [Category](url) research tree unlocks [Item](url)."
    def _repl_intro(m):
        cat_link, item_link = m.group(1), m.group(2)
        return (t(lang, "techtree", "node_intro")
                .replace("{category_link}", cat_link)
                .replace("{item_link}", item_link))

    c = re.sub(r'This node of the (\[[^\]]+\]\([^)]+\)) research tree unlocks (\[[^\]]+\]\([^)]+\))\.', _repl_intro, c)

    # Plain-text item variant (items not in the catalog, e.g. node foundations)
    def _repl_intro_plain(m):
        cat_link, name = m.group(1), m.group(2)
        return (t(lang, "techtree", "node_intro_plain")
                .replace("{category_link}", cat_link)
                .replace("{name}", name))

    c = re.sub(
        r'This node of the (\[[^\]]+\]\([^)]+\)) research tree unlocks ([^.]+?)\.', _repl_intro_plain, c)

    # "– (end of line)" table values
    c = c.replace("– (end of line)", t(lang, "techtree", "node_end_of_line"))

    for field, key in [
        ("Category", "labels.category"), ("Unlocks", "techtree.unlocks"),
        ("Parent node", "techtree.parent_node"), ("Unlocks next", "techtree.unlocks_next"),
        ("Enabler extension", "techtree.enabler_extension"), ("Point prices", "techtree.point_prices"),
    ]:
        f_tr = t(lang, *key.split("."))
        c = re.sub(rf'\|\s*{field}\s*\|', f'| {f_tr} |', c)

    all_nodes = t(lang, "techtree", "all_nodes")
    c = re.sub(r'\[All tech tree nodes\]\([^)]+\)', f'[{all_nodes}](/{lang}/content/techtree/)', c)

    return c


def process_recipes_file(content, lang):
    """Translate recipes.md (2.9 MB)."""
    c = rewrite_links(content, lang)
    recipes_tr = t(lang, "ui", "nav_content_recipes")
    c = re.sub(r'title:\s*"Recipes"', f'title: "{recipes_tr}"', c)
    c = re.sub(r'^#\s*Recipes', f'# {recipes_tr}', c, flags=re.MULTILINE)

    res_lvl = t(lang, "missions", "research_level")
    c = re.sub(r'<div class="mission-card-sub">Research level\s+(\d+)</div>',
               rf'<div class="mission-card-sub">{res_lvl} \1</div>', c)

    # Intro paragraph
    c = re.sub(
        r'Component requirements for every item that is assembled from other items, grouped by category \(see (\[Production\]\([^)]+\)) in the features section\)\. \*\*Research level\*\* is the maximum research level the item has — higher levels change yield/calibration, not the component list\. Each item has its own page with its stats, the items it is a component of, and the vendors that sell it\.',
        lambda m: t(lang, "recipes", "intro").replace("{production_link}", m.group(1)), c
    )

    return c


def process_missions_file(content, lang):
    """Translate missions.md."""
    c = rewrite_links(content, lang)
    missions_tr = t(lang, "ui", "nav_content_missions")
    c = re.sub(r'title:\s*"Missions"', f'title: "{missions_tr}"', c)
    c = re.sub(r'^#\s*Missions', f'# {missions_tr}', c, flags=re.MULTILINE)

    lvl_tr = t(lang, "missions", "level")
    c = re.sub(r'<div class="mission-card-title">Level\s+(\d+)</div>',
               rf'<div class="mission-card-title">{lvl_tr} \1</div>', c)

    fee_tr = t(lang, "missions", "reward_fee")
    c = re.sub(r'<div class="mission-card-sub">Reward fee\s+([^<]+)</div>',
               rf'<div class="mission-card-sub">{fee_tr} \1</div>', c)

    dur_tr = t(lang, "missions", "duration")
    min_tr = t(lang, "missions", "min")
    c = re.sub(r'<div class="mission-card-sub">Duration\s+(\d+)\s+min</div>',
               rf'<div class="mission-card-sub">{dur_tr} \1 {min_tr}</div>', c)

    # Intro paragraph
    c = re.sub(
        r'One section per \*\*mission type\*\*; each tier is a card\. \*\*Reward fee\*\* is the credit payout \(a range when a tier has several zone variants\); \*\*rewards\*\* are the item drops \(quantity range and drop probability, 100 = guaranteed\)\. See (\[Missions\]\([^)]+\)) in the features section for how missions work\.',
        lambda m: t(lang, "missions", "intro").replace("{missions_link}", m.group(1)), c
    )

    return c


def process_extensions_file(content, lang):
    """Translate extensions.md."""
    c = rewrite_links(content, lang)
    ext_tr = t(lang, "ui", "nav_extensions")
    c = re.sub(r'title:\s*"Extensions"', f'title: "{ext_tr}"', c)
    c = re.sub(r'^#\s*Extensions', f'# {ext_tr}', c, flags=re.MULTILINE)

    rank_tr = t(lang, "extensions", "rank")
    c = re.sub(r'<span class="ext-val-rank">rank\s+(\d+)</span>',
               rf'<span class="ext-val-rank">{rank_tr} \1</span>', c)

    bonus_tr = t(lang, "extensions", "bonus")
    c = re.sub(r'<span class="ext-val-bonus">bonus\s+([^<]+)</span>',
               rf'<span class="ext-val-bonus">{bonus_tr} \1</span>', c)

    inact_tr = t(lang, "extensions", "inactive")
    c = re.sub(r'·\s*inactive', f'· {inact_tr}', c)

    nopreq_tr = t(lang, "extensions", "no_prerequisites")
    c = re.sub(r'<div class="ext-card-prereq">no prerequisites</div>',
               rf'<div class="ext-card-prereq">{nopreq_tr}</div>', c)

    # Intro paragraph
    c = re.sub(
        r'Extensions are the per-character skill tree — learned with credits \(level 1\) and EP \(later levels\), gated by prerequisites\. See (\[Character\]\([^)]+\)) for the character window this tree lives in\. The spark extensions \(the passive specialization lines\) have their own diagram on the (\[Sparks\]\([^)]+\)) page\.',
        lambda m: t(lang, "extensions", "intro").replace("{character_link}", m.group(1)).replace("{sparks_link}", m.group(2)), c
    )

    # Overview paragraph (count + Sparks link captured)
    c = re.sub(
        r'The (\d+) categories at a glance: one box per category \(extension count, entry points without prerequisites, rank range\), left to right by starting rank, and an arrow for every cross-category prerequisite \(hover an arrow for the exact requirements\) — which categories open up which\. \*\*Click a box to jump to that category.s cards below\.\*\* The spark extensions sit outside this diagram \(no prerequisites of their own\) — their bundle diagram is on the (\[Sparks\]\([^)]+\)) page\. \*\*Scroll over the diagram to zoom\*\*, drag to pan, and use the ⟲ button to reset\.',
        lambda m: t(lang, "extensions", "overview").replace("{count}", m.group(1)).replace("{sparks_link}", m.group(2)), c
    )

    # Legend paragraph
    c = c.replace(
        "One section per category, one card per extension. **Price** is the level-1 credit cost (later levels cost EP only). **Prerequisites** are the extensions (and minimum level) to learn first. Inactive entries are not offered by the current server build.",
        t(lang, "extensions", "legend")
    )

    return c


def process_content_overview(content, lang):
    """Translate content/_index.md."""
    c = rewrite_links(content, lang)
    content_tr = t(lang, "ui", "foot_content")
    c = re.sub(r'title:\s*"Content"', f'title: "{content_tr}"', c)
    c = re.sub(r'^#\s*Content', f'# {content_tr}', c, flags=re.MULTILINE)

    c = c.replace(
        "Stat tables for every content entity, generated from the live database.",
        t(lang, "content_index", "stat_tables")
    )
    # Field-meanings line (Formats link captured)
    c = re.sub(
        r'Field meanings \(what a stat column actually does\) live in (\[Formats\]\([^)]+\))\.',
        lambda m: t(lang, "content_index", "field_meanings").replace("{formats_link}", m.group(1)), c
    )
    return c


def process_ores_overview(content, lang):
    """Translate content/ores.md."""
    c = rewrite_links(content, lang)
    ores_tr = t(lang, "ui", "nav_content_ores")
    c = re.sub(r'title:\s*"Ores"', f'title: "{ores_tr}"', c)
    c = re.sub(r'^#\s*Ores', f'# {ores_tr}', c, flags=re.MULTILINE)

    ore_types_tr = t(lang, "ores", "ore_types")
    c = c.replace("## Ore types", f"## {ore_types_tr}")

    c = c.replace("<th>Ore</th>", f"<th>{t(lang, 'ores', 'ore')}</th>")
    c = c.replace("<th>Amount / extraction</th>", f"<th>{t(lang, 'ores', 'amount_extraction')}</th>")
    c = c.replace("<th>Extraction type</th>", f"<th>{t(lang, 'ores', 'extraction_type')}</th>")
    c = c.replace("<th>Enabler effect</th>", f"<th>{t(lang, 'ores', 'enabler_effect')}</th>")
    c = c.replace("<th>Geo-scan doc</th>", f"<th>{t(lang, 'ores', 'geo_scan_doc')}</th>")

    c = c.replace("<td>no</td>", f"<td>{t(lang, 'labels', 'no')}</td>")
    c = c.replace("<td>required</td>", f"<td>{t(lang, 'ores', 'required')}</td>")

    # Intro paragraph (Ore-fields link captured)
    c = re.sub(
        r'Ore exists in the ground as \*\*deposits \(nodes\)\*\*\. Each node holds a limited total amount; when a node is mined below its threshold it is removed and the zone regenerates new nodes up to its configured maximum\. Every ore has its own page with its extraction facts, the zones it spawns in and what is made from it\. How each column is used by the server, with the node-generation formulas, is in (\[Ore fields\]\([^)]+\))\.',
        lambda m: t(lang, "ores", "intro").replace("{ore_fields_link}", m.group(1)), c
    )

    # Extraction-type legend paragraph
    c = c.replace(
        "**Extraction type**: 0 = solid (tile-by-tile with a drill), 1 = liquid (continuous pump). **Enabler effect** — when *required*, the robot needs the matching enabler effect active to extract that ore at all. How many nodes of each ore a zone maintains, and how large each node is, is on each ore's own page (the *Zone parameters* table there).",
        t(lang, "ores", "legend")
    )
    return c


def process_plants_overview(content, lang):
    """Translate content/plants.md."""
    c = rewrite_links(content, lang)
    plants_tr = t(lang, "ui", "nav_content_plants")
    c = re.sub(r'title:\s*"Plants"', f'title: "{plants_tr}"', c)
    c = re.sub(r'^#\s*Plants', f'# {plants_tr}', c, flags=re.MULTILINE)

    P = lambda key: t(lang, "plants", key)

    # Growth-cycle diagram (mermaid): translate node labels only; the flow
    # structure (node ids, edges) stays identical. The respawn label keeps its
    # literal two-character \n, which mermaid renders as a line break.
    for en_label, key in [
        ("Sprout (stage 1)", "diagram_sprout"),
        ("Grow: growRate cycles per stage", "diagram_grow"),
        ("Fruiting stage reached", "diagram_fruiting"),
        ("Harvestable: fruit x fruitAmount", "diagram_harvestable"),
        ("Killed / damaged", "diagram_killed"),
        ("Zone respawns toward the\\nfertility target (weighted by species fertility)", "diagram_respawn"),
    ]:
        c = c.replace(f'["{en_label}"]', f'["{P(key)}"]')

    c = c.replace("## Harvestable plants", f"## {P('harvestable')}")
    c = c.replace(
        "Species with a fruiting stage — the fruit is the harvestable yield (× = fruitAmount per fruiting stage).",
        P("harvestable_intro")
    )
    c = c.replace(
        "| Plant | Grow rate | Fertility | Spreading | Kill distance | Max slope | Altitude band | Water band | Fruit (yield) | Max amount | Health (stages) | Player seeded |",
        f"| {P('col_plant')} | {P('col_grow_rate')} | {P('col_fertility')} | {P('col_spreading')} | "
        f"{P('col_kill_distance')} | {P('col_max_slope')} | {P('col_altitude_band')} | {P('col_water_band')} | "
        f"{P('col_fruit_yield')} | {P('col_max_amount')} | {P('col_health_stages')} | {P('col_player_seeded')} |"
    )

    c = c.replace("## Scenery plants (not harvestable)", f"## {P('scenery')}")
    c = c.replace(
        "Species with no fruiting stage — zone scenery only (cover, landmarks, blocking).",
        P("scenery_intro")
    )
    c = c.replace(
        "| Plant | Grow rate | Fertility | Spreading | Kill distance | Max slope | Altitude band | Water band | Max amount | Health (stages) | Player seeded |",
        f"| {P('col_plant')} | {P('col_grow_rate')} | {P('col_fertility')} | {P('col_spreading')} | "
        f"{P('col_kill_distance')} | {P('col_max_slope')} | {P('col_altitude_band')} | {P('col_water_band')} | "
        f"{P('col_max_amount')} | {P('col_health_stages')} | {P('col_player_seeded')} |"
    )

    c = c.replace("## Zones", f"## {P('zones_heading')}")
    c = c.replace(
        "| Zone | Type | Protected | Fertility | Plant ruleset | Altitude scale | Enabled |",
        f"| {t(lang, 'ores', 'col_zone')} | {P('col_type')} | {P('col_protected')} | {P('col_fertility')} | "
        f"{P('col_plant_ruleset')} | {P('col_altitude_scale')} | {P('col_enabled')} |"
    )

    c = c.replace("## Ruleset → species", f"## {P('ruleset_heading')}")
    c = c.replace(
        "| Ruleset | Zones | Species |",
        f"| {P('col_ruleset')} | {P('col_zones')} | {P('col_species')} |"
    )

    yes_tr = t(lang, "labels", "yes")
    no_tr = t(lang, "labels", "no")
    c = re.sub(r'\| yes \|', f'| {yes_tr} |', c)
    c = re.sub(r'\| no \|', f'| {no_tr} |', c)

    # Intro paragraph (Plant-fields link captured)
    c = re.sub(
        r'Plants grow over time through a sequence of stages; a plant produces \(is harvestable\) only once it reaches its fruiting stage\. The zone maintains plant populations toward a \*\*fertility target\*\* per area; `spreading` biases new growth toward existing clusters of the same type\. The full field reference — types, defaults, the growth state machine, and the rule-file format — is in (\[Plant fields\]\([^)]+\))\.',
        lambda m: t(lang, "plants", "intro").replace("{plant_fields_link}", m.group(1)), c
    )

    # Field-meanings legend (plain line, ends with ";")
    c = c.replace(
        "Field meanings: **growRate** = growth cycles a plant sits in each stage before advancing (higher = slower); **fertility** = how strongly the zone tries to keep this species present; **spreading** = preference for growing in groups; **killDistance** = minimum spacing between two plants of the same type (−1 = none);",
        t(lang, "plants", "fields_legend")
    )

    # Zones-section legend
    c = c.replace(
        "Per-zone fertility (how full the ground is kept with plants), the plant ruleset the zone uses, and altitude scaling.",
        t(lang, "plants", "zones_legend")
    )

    return c


# (heading name, category key, description key) for the deployables.md sections
DEPLOYABLE_SECTIONS = [
    ("Mobile teleports", "cat_mobile_tps", "desc_mobile_tps"),
    ("Mobile fields", "cat_mobile_fields", "desc_mobile_fields"),
    ("Arena teleports", "cat_arena_tps", "desc_arena_tps"),
    ("Mines & bombs", "cat_mines", "desc_mines"),
    ("Wall repairers", "cat_wall", "desc_wall"),
    ("Plant seeds", "cat_seeds", "desc_seeds"),
    ("NPC eggs", "cat_eggs", "desc_eggs"),
    ("Gates", "cat_gates", "desc_gates"),
    ("Containers", "cat_containers", "desc_containers"),
    ("Miscellaneous", "cat_misc", "desc_misc"),
]


def process_deployables_overview(content, lang):
    """Translate content/deployables.md."""
    c = rewrite_links(content, lang)
    dep_tr = t(lang, "ui", "nav_content_deployables")
    c = re.sub(r'title:\s*"Deployables"', f'title: "{dep_tr}"', c)
    c = re.sub(r'^#\s*Deployables', f'# {dep_tr}', c, flags=re.MULTILINE)

    no_tier_tr = t(lang, "labels", "no_tier")
    c = re.sub(r'<div class="prod-card-body">no tier</div>',
               rf'<div class="prod-card-body">{no_tier_tr}</div>', c)

    # Intro paragraph (count + PBS and Deployable-fields links captured)
    c = re.sub(
        r'Deployables are items that can be \*\*placed in the terrain\*\* to act on the zone — effect suppliers, repairers, turrets, teleports, and similar\. Placing one is a corporation/privilege-gated action\. The (\d+) non-PBS deployables are listed below, one page each: \*\*click a card to open it\.\*\* The PBS structures are documented on the (\[Power base stations\]\([^)]+\)) page\. How deployables are identified, paired capsule↔object, and which stat fields drive them is in (\[Deployable fields\]\([^)]+\))\.',
        lambda m: (t(lang, "deployables", "intro")
                   .replace("{count}", m.group(1))
                   .replace("{pbs_link}", m.group(2))
                   .replace("{dep_fields_link}", m.group(3))), c
    )

    # Category headings "## Name (N)" and their description paragraphs
    for name, cat_key, desc_key in DEPLOYABLE_SECTIONS:
        head_tr = t(lang, "deployables", "cat_heading").replace("{category}", t(lang, "deployables", cat_key))
        c = re.sub(rf'^## {re.escape(name)} \((\d+)\)$',
                   lambda m, h=head_tr: "## " + h.replace("{count}", m.group(1)),
                   c, flags=re.MULTILINE)
        desc_tr = t(lang, "deployables", desc_key)
        if "{teleporting_link}" in desc_tr:
            c = re.sub(r'Deployable teleports a player places in the terrain \(see (\[Teleporting\]\([^)]+\))\)\.',
                       lambda m, d=desc_tr: d.replace("{teleporting_link}", m.group(1)), c)
        elif "{plants_link}" in desc_tr:
            c = re.sub(r'Seeds that grow the matching plant species when planted \(see (\[Plants\]\([^)]+\))\)\.',
                       lambda m, d=desc_tr: d.replace("{plants_link}", m.group(1)), c)
        elif "{egg_shop_link}" in desc_tr:
            c = re.sub(r'Capsules that hatch an NPC unit when placed \(bought in the (\[NPC egg shop\]\([^)]+\))\)\.',
                       lambda m, d=desc_tr: d.replace("{egg_shop_link}", m.group(1)), c)
        else:
            # plain description: match the exact English sentence for this section
            en_desc = {
                "desc_mobile_fields": "Deployable effect fields: ECCM, maskers and the reactor stabilizer.",
                "desc_arena_tps": "Teleport devices that move combatants and audience between the arena and the outer zones.",
                "desc_mines": "Deployed explosives: the landmine sizes, wall bombs, the area bomb and plant bombs.",
                "desc_wall": "Deployed repairers that heal the wall structures.",
                "desc_gates": "The zone gate capsule.",
                "desc_containers": "The deployable container capsule.",
                "desc_misc": "Everything else that can be placed in the terrain: beacons, probes, buoys, and the test deployables.",
            }.get(desc_key)
            if en_desc:
                c = c.replace(en_desc, desc_tr)

    return c


ROBOT_CLASSES = [
    ("Runners", "runners"),
    ("Crawlers", "crawlers"),
    ("Mechs", "mechs"),
    ("Heavy mechs", "heavy_mechs"),
    ("Walkers", "walkers"),
]

ROBOT_SUBSECTION_DESCRIPTIONS = [
    ("The fast, light class — the cheapest robots to build and pilot.", "runners_desc"),
    ("The mid-size workhorse class.", "crawlers_desc"),
    ("The main combat class.", "mechs_desc"),
    ("The top-tier combat class.", "heavy_mechs_desc"),
    ("A rare heavy platform class.", "walkers_desc"),
    ("The starter bot, the flagship and limited/event models.", "starter_special_desc"),
    ("Complete cult-designed loadouts unlocked through research — a finished fit rather than a standalone chassis (size comes from the parts it is built from).", "named_fits_desc"),
    ("*Strengths:* a ready-made combat build with its role in the name (main combat / main support).", "named_fits_strengths"),
    ("*Weaknesses:* fixed by the design — you take the fit as it comes.", "named_fits_weaknesses"),
    ("Mixed-class builds assembled from parts of different robot classes rather than one pure class. They are built from parts, not sold as a finished robot; the finished size comes from the parts chosen.", "hybrid_builds_desc"),
    ("*Strengths:* mix the advantages of several classes in one build.", "hybrid_builds_strengths"),
    ("*Weaknesses:* you must assemble the parts yourself — no single finished product to buy.", "hybrid_builds_weaknesses"),
    ("Combat units fielded by the NPC factions (not acquirable by players).", "npc_units_desc"),
]


def process_robots_overview(content, lang):
    """Translate content/robots.md."""
    c = rewrite_links(content, lang)
    robots_tr = t(lang, "ui", "home_robots")
    c = re.sub(r'title:\s*"Robots"', f'title: "{robots_tr}"', c)
    c = re.sub(r'^#\s*Robots', f'# {robots_tr}', c, flags=re.MULTILINE)

    desc_tr = t(lang, "robots", "index_desc")
    c = re.sub(r'description:\s*"[^"]*"', f'description: "{desc_tr}"', c)

    intro_tr = t(lang, "robots", "index_intro")
    intro_tr = intro_tr.replace("{lang}", lang)
    c = re.sub(r'Fitting, slots and in-game play are covered in the \[Robot\]\([^)]+\) feature page; this page is the data reference\.', intro_tr, c)

    c = c.replace("## Robot classes", f"## {t(lang, 'robots', 'robot_classes')}")
    c = c.replace(
        "A robot's class comes from its parts. Ratings are 1–5 (more icons = higher).",
        t(lang, "robots", "class_intro")
    )

    # Class ratings table
    c = c.replace("<th>Class</th>", f"<th>{t(lang, 'labels', 'class')}</th>")
    for stat in ["combat", "speed", "armor", "storage", "cost"]:
        stat_tr = t(lang, "labels", stat)
        c = re.sub(rf'<th>{stat.capitalize()}</th>', f'<th>{stat_tr}</th>', c)
        c = re.sub(rf'<span>{stat.capitalize()}</span>', f'<span>{stat_tr}</span>', c)

    # Table rows class names
    for cls, key in ROBOT_CLASSES:
        c = c.replace(f"<b>{cls}</b>", f"<b>{t(lang, 'robots', key)}</b>")

    c = c.replace("## Player robots", f"## {t(lang, 'robots', 'player_robots')}")
    c = c.replace(
        "Robots you can acquire and control yourself (80 models), grouped by class.",
        t(lang, "robots", "player_robots_intro")
    )

    # Subsection headings
    c = c.replace("### Runners (20)", f"### {t(lang, 'robots', 'runners')} (20)")
    c = c.replace("### Crawlers (11)", f"### {t(lang, 'robots', 'crawlers')} (11)")
    c = c.replace("### Mechs (19)", f"### {t(lang, 'robots', 'mechs')} (19)")
    c = c.replace("### Heavy mechs (18)", f"### {t(lang, 'robots', 'heavy_mechs')} (18)")
    c = c.replace("### Walkers (2)", f"### {t(lang, 'robots', 'walkers')} (2)")
    c = c.replace("### Starter & special (10)", f"### {t(lang, 'robots', 'starter_special')} (10)")
    c = c.replace("### Named fits (3)", f"### {t(lang, 'robots', 'named_fits')} (3)")
    c = c.replace("## Hybrid builds (27)", f"## {t(lang, 'robots', 'hybrid_builds')} (27)")
    c = c.replace("## NPC units (1)", f"## {t(lang, 'robots', 'npc_units')} (1)")

    # Subsection descriptions
    for desc, key in ROBOT_SUBSECTION_DESCRIPTIONS:
        c = c.replace(desc, t(lang, "robots", key))

    # Named fits table header
    c = c.replace("| Robot | Class |", f"| {t(lang, 'labels', 'robot')} | {t(lang, 'labels', 'class')} |")

    # Card status labels
    c = c.replace("<span>Stats vary by parts</span>", f"<span>{t(lang, 'robots', 'stats_vary')}</span>")
    c = c.replace("<span>NPC unit — not player-acquirable</span>", f"<span>{t(lang, 'robots', 'npc_not_acquirable')}</span>")

    return c


def process_techtree_overview(content, lang):
    """Translate content/techtree/_index.md."""
    c = rewrite_links(content, lang)
    tt_tr = t(lang, "ui", "nav_content_techtree")
    c = re.sub(r'title:\s*"Tech tree"', f'title: "{tt_tr}"', c)
    c = re.sub(r'^#\s*Tech tree', f'# {tt_tr}', c, flags=re.MULTILINE)

    # Intro paragraph (Research link captured)
    c = re.sub(
        r'Tech tree nodes unlock items by spending \*\*research points\*\* \(earned from kernels — see (\[Research\]\([^)]+\)) in the features section\)\. A node can only be unlocked when its \*\*parent\*\* node is unlocked and the \*\*enabler extension\*\* is learned\. Point types: common, hitech, industrial, newtech, nuimqol, pelistal, thelodica\.',
        lambda m: t(lang, "techtree", "index_intro").replace("{research_link}", m.group(1)), c
    )

    c = c.replace(
        "Each category is its own page with the full tree and one page per node.",
        t(lang, "techtree", "index_cats_line")
    )

    c = c.replace("## Categories", f"## {t(lang, 'techtree', 'categories')}")
    return c


def process_shop_overview(content, lang):
    """Translate content/shop.md."""
    c = rewrite_links(content, lang)
    shop_tr = t(lang, "ui", "nav_shop")
    c = re.sub(r'title:\s*"Item shop"', f'title: "{shop_tr}"', c)
    c = re.sub(r'^#\s*Item shop', f'# {shop_tr}', c, flags=re.MULTILINE)

    # Intro paragraph (market + robot-catalog links captured)
    c = re.sub(
        r'Fixed-price vendor items, separate from the player-driven (\[market\]\([^)]+\))\. The same item can be sold at several vendors — the catalog below lists every item once, with the best price across all vendors; each item.s own page lists every vendor that sells it \(robots link to the (\[robot catalog\]\([^)]+\))\)\.',
        lambda m: t(lang, "shop", "intro").replace("{market_link}", m.group(1)).replace("{robots_link}", m.group(2)), c
    )

    # Currencies legend (overview variant)
    c = c.replace(
        "**Currencies** — **TM Coin / ICS Coin / ASI Coin**: the per-galaxy shop currency (each shop sells for all three coins where offered); **Credits**: the common currency; **UniCoin**: a premium currency. **Qty ∞** means the vendor has no stock limit.",
        t(lang, "shop", "currency_legend_overview")
    )

    c = c.replace(
        "Each category is its own page; best price across all vendors, one row per item.",
        t(lang, "shop", "cats_line")
    )

    c = c.replace("## Vendors", f"## {t(lang, 'shop', 'vendors')}")
    c = c.replace("## Catalog", f"## {t(lang, 'shop', 'catalog')}")
    return c


def process_stat_reference_file(content, lang):
    """Translate content/stat-reference.md."""
    c = rewrite_links(content, lang)
    stat_tr = t(lang, "ui", "nav_content_statref")
    c = re.sub(r'title:\s*"Stat reference"', f'title: "{stat_tr}"', c)
    c = re.sub(r'^#\s*Stat reference', f'# {stat_tr}', c, flags=re.MULTILINE)

    c = c.replace(
        "Every item page lists raw stat values. This page puts them in scale: the unit of each stat, the smallest/largest values in the whole catalog, and real items to compare against. Ranges are computed over all enabled items (prototypes and test objects excluded).",
        t(lang, "stat_reference", "intro")
    )

    c = c.replace("## Powergrid and CPU in context", f"## {t(lang, 'stat_reference', 'heading_pg_cpu')}")

    c = c.replace(
        "A module's **powergrid_usage** is only meaningful against the robot that carries it: the chassis defines the total RP (**powergrid_max**), energy (**core_max**) and CPU (**cpu_max**) its modules may use. **Powergrid upgrades** modules add a fixed amount of RP. A usage value is a percentage of the available capacity — for example a module with powergrid_usage 214 uses 214% of an Ikarus chassis (100 RP, nothing fits beyond the frame) but only ~3% of an Onyx chassis (6.6k RP).",
        t(lang, "stat_reference", "pg_context")
    )

    c = c.replace(
        "For each documented stat: how many items have it, its unit, and the smallest / median / largest value in the catalog with an item you can open at each end.",
        t(lang, "stat_reference", "per_stat")
    )

    # "not listed" paragraph (Formats link captured)
    c = re.sub(
        r'Stats not listed here are either \*\*modifier\*\* stats \(they change another stat instead of setting one\) or internal values without a player-facing unit — the developer field reference in (\[Formats\]\([^)]+\)) lists every field\.',
        lambda m: t(lang, "stat_reference", "not_listed").replace("{formats_link}", m.group(1)), c
    )
    return c


def main():
    root = Path(".")
    src_content_dir = root / "content" / "content"

    if not src_content_dir.exists():
        print(f"gen_content_translations: source directory {src_content_dir} not found!", file=sys.stderr)
        sys.exit(1)

    t0 = time.time()
    total_written = 0

    for lang in LANGUAGES:
        dest_dir = root / "content" / lang / "content"
        dest_dir.mkdir(parents=True, exist_ok=True)

        # 1. Section index: _index.md
        src_idx = src_content_dir / "_index.md"
        if src_idx.exists():
            content = process_content_overview(src_idx.read_text(encoding="utf-8"), lang)
            (dest_dir / "_index.md").write_text(content, encoding="utf-8")
            total_written += 1

        # 2. Ores overview & individual ore pages
        src_ores = src_content_dir / "ores.md"
        if src_ores.exists():
            content = process_ores_overview(src_ores.read_text(encoding="utf-8"), lang)
            (dest_dir / "ores.md").write_text(content, encoding="utf-8")
            total_written += 1

        src_ores_dir = src_content_dir / "ores"
        dest_ores_dir = dest_dir / "ores"
        if src_ores_dir.exists():
            dest_ores_dir.mkdir(exist_ok=True)
            for f in src_ores_dir.glob("*.md"):
                content = process_ore_file(f.read_text(encoding="utf-8"), lang)
                (dest_dir / "ores" / f.name).write_text(content, encoding="utf-8")
                total_written += 1

        # 3. Plants
        src_plants = src_content_dir / "plants.md"
        if src_plants.exists():
            content = process_plants_overview(src_plants.read_text(encoding="utf-8"), lang)
            (dest_dir / "plants.md").write_text(content, encoding="utf-8")
            total_written += 1

        # 4. Missions
        src_missions = src_content_dir / "missions.md"
        if src_missions.exists():
            content = process_missions_file(src_missions.read_text(encoding="utf-8"), lang)
            (dest_dir / "missions.md").write_text(content, encoding="utf-8")
            total_written += 1

        # 5. Deployables overview & individual pages
        src_dep = src_content_dir / "deployables.md"
        if src_dep.exists():
            content = process_deployables_overview(src_dep.read_text(encoding="utf-8"), lang)
            (dest_dir / "deployables.md").write_text(content, encoding="utf-8")
            total_written += 1

        src_dep_dir = src_content_dir / "deployables"
        dest_dep_dir = dest_dir / "deployables"
        if src_dep_dir.exists():
            dest_dep_dir.mkdir(exist_ok=True)
            for f in src_dep_dir.glob("*.md"):
                content = process_deployable_file(f.read_text(encoding="utf-8"), lang)
                (dest_dep_dir / f.name).write_text(content, encoding="utf-8")
                total_written += 1

        # 6. Robots overview & individual robot pages
        src_robots = src_content_dir / "robots.md"
        if src_robots.exists():
            content = process_robots_overview(src_robots.read_text(encoding="utf-8"), lang)
            (dest_dir / "robots.md").write_text(content, encoding="utf-8")
            total_written += 1

        src_robots_dir = src_content_dir / "robots"
        dest_robots_dir = dest_dir / "robots"
        if src_robots_dir.exists():
            dest_robots_dir.mkdir(exist_ok=True)
            for f in src_robots_dir.glob("*.md"):
                content = process_robot_file(f.read_text(encoding="utf-8"), lang)
                (dest_robots_dir / f.name).write_text(content, encoding="utf-8")
                total_written += 1

        # 7. Recipes (2.9 MB)
        src_recipes = src_content_dir / "recipes.md"
        if src_recipes.exists():
            content = process_recipes_file(src_recipes.read_text(encoding="utf-8"), lang)
            (dest_dir / "recipes.md").write_text(content, encoding="utf-8")
            total_written += 1

        # 8. Tech tree overview & groups
        dest_tt_dir = dest_dir / "techtree"
        dest_tt_dir.mkdir(exist_ok=True)
        src_tt_idx = src_content_dir / "techtree" / "_index.md"
        if src_tt_idx.exists():
            content = process_techtree_overview(src_tt_idx.read_text(encoding="utf-8"), lang)
            (dest_tt_dir / "_index.md").write_text(content, encoding="utf-8")
            total_written += 1

        src_tt_grp_dir = src_content_dir / "techtree" / "groups"
        dest_tt_grp_dir = dest_tt_dir / "groups"
        if src_tt_grp_dir.exists():
            dest_tt_grp_dir.mkdir(exist_ok=True)
            for f in src_tt_grp_dir.glob("*.md"):
                content = process_techtree_group_file(f.read_text(encoding="utf-8"), lang)
                (dest_tt_grp_dir / f.name).write_text(content, encoding="utf-8")
                total_written += 1

        src_tt_node_dir = src_content_dir / "techtree" / "nodes"
        dest_tt_node_dir = dest_tt_dir / "nodes"
        if src_tt_node_dir.exists():
            dest_tt_node_dir.mkdir(exist_ok=True)
            for f in src_tt_node_dir.glob("*.md"):
                content = process_techtree_node_file(f.read_text(encoding="utf-8"), lang)
                (dest_tt_node_dir / f.name).write_text(content, encoding="utf-8")
                total_written += 1

        # 9. Extensions
        src_ext = src_content_dir / "extensions.md"
        if src_ext.exists():
            content = process_extensions_file(src_ext.read_text(encoding="utf-8"), lang)
            (dest_dir / "extensions.md").write_text(content, encoding="utf-8")
            total_written += 1

        # 10. Stat reference
        src_stat = src_content_dir / "stat-reference.md"
        if src_stat.exists():
            content = process_stat_reference_file(src_stat.read_text(encoding="utf-8"), lang)
            (dest_dir / "stat-reference.md").write_text(content, encoding="utf-8")
            total_written += 1

        # 11. Shop overview & categories
        src_shop = src_content_dir / "shop.md"
        if src_shop.exists():
            content = process_shop_overview(src_shop.read_text(encoding="utf-8"), lang)
            (dest_dir / "shop.md").write_text(content, encoding="utf-8")
            total_written += 1

        src_shop_dir = src_content_dir / "shop"
        dest_shop_dir = dest_dir / "shop"
        if src_shop_dir.exists():
            dest_shop_dir.mkdir(exist_ok=True)
            for f in src_shop_dir.glob("*.md"):
                content = process_shop_file(f.read_text(encoding="utf-8"), lang)
                (dest_shop_dir / f.name).write_text(content, encoding="utf-8")
                total_written += 1

    elapsed = time.time() - t0
    print(f"gen_content_translations: wrote {total_written} localized files across {len(LANGUAGES)} languages in {elapsed:.2f}s")


if __name__ == "__main__":
    main()
