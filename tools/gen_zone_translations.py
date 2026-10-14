#!/usr/bin/env python3
"""Generate localized zone pages in content/<lang>/zones/ for all 13 supported languages.

Generates:
- content/<lang>/zones/_index.md        (from translations/<lang>.json)
- content/<lang>/zones/protection.md    (from translations/<lang>.json)
- content/<lang>/zones/alpha.md
- content/<lang>/zones/beta.md
- content/<lang>/zones/gamma.md
- content/<lang>/zones/zone-index.md
- content/<lang>/zones/map.md
- All 79 generated content/<lang>/zones/zone_*.md pages

All translatable strings come from translations/<lang>.json (single source of
truth, see tools/i18n_common.py); missing keys fall back to English.

Preserves hand-written worked examples (generation.md, zone_tm.md, zone_asi.md,
zone_gamma_z106.md) when already present. Rewrites all internal links to
/{lang}/ routes.
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

# Frontmatter description protection words -> zones.* keys
PROT_KEYS = {
    "protected": "protected",
    "open-terraformable": "open_terraformable",
    "open": "open",
    "": "",
}


# The 7 zone intro templates (matched against the English source paragraph,
# {fam} = zone family, {n} = ore type count)
def translate_intro(text, lang):
    # Match: "A protected (Alpha) {fam} zone — safe from player attack, ..."
    m = re.search(r'A protected \(Alpha\) (.*?) zone — safe from player attack, the standard gathering ground for the \1 galaxy\.', text)
    if m:
        res = t(lang, "zones", "intro", "alpha_protected").replace("{fam}", m.group(1))
        return append_maintains(res, text, lang)

    # Match: "An open-PvP (beta) {fam} island — players can attack freely and blobs apply."
    m = re.search(r'An open-PvP \(beta\) (.*?) island — players can attack freely and blobs apply\.', text)
    if m:
        res = t(lang, "zones", "intro", "beta_open").replace("{fam}", m.group(1))
        return append_maintains(res, text, lang)

    # Match: "An open-PvP, terraformable (gamma) {fam} island — the ground can be reshaped by players."
    m = re.search(r'An open-PvP, terraformable \(gamma\) (.*?) island — the ground can be reshaped by players\.', text)
    if m:
        res = t(lang, "zones", "intro", "gamma_terraformable").replace("{fam}", m.group(1))
        return append_maintains(res, text, lang)

    # Match: "A small transit zone of the frontier belt — a pure travel node with no ore configuration."
    if "small transit zone of the frontier belt" in text:
        return t(lang, "zones", "intro", "frontier_transit")

    # Match: "The virtual training island — where new characters start and learn the basics."
    if "virtual training island" in text:
        return t(lang, "zones", "intro", "training")

    # Match: "The PvP arena — a scripted combat event zone."
    if "The PvP arena" in text:
        return t(lang, "zones", "intro", "arena")

    # Match: "A stronghold — a protected instance zone with its own exit gate."
    if "A stronghold" in text:
        return t(lang, "zones", "intro", "stronghold")

    return text


def append_maintains(translated_base, original_full, lang):
    m = re.search(r'It maintains (\d+) ore types?\.', original_full)
    if not m:
        return translated_base
    n = m.group(1)
    return translated_base + t(lang, "zones", "maintains_ore_types").replace("{n}", n)


def rewrite_zone_links(text, lang):
    """Rewrite /zones/ and /content/ links to /{lang}/ while keeping /content/items/ and assets untouched."""
    # /zones/...
    def repl_zones(m):
        path = m.group(1)
        # Don't prefix if already prefixed
        if path.startswith(f"/{lang}/"):
            return m.group(0)
        return f"({path[:1]}{lang}{path[1:]})"

    # Match markdown link targets: (/zones/...) -> (/{lang}/zones/...)
    text = re.sub(r'\((/zones/[^)]*)\)', rf'(/{lang}\1)', text)
    # Match href="/zones/...": href="/{lang}/zones/..."
    text = re.sub(r'href="(/zones/[^"]*)"', rf'href="/{lang}\1"', text)

    # Match /content/ores/... links
    text = re.sub(r'\((/content/ores/[^)]*)\)', rf'(/{lang}\1)', text)
    text = re.sub(r'href="(/content/ores/[^"]*)"', rf'href="/{lang}\1"', text)

    return text


def process_generated_zone_page(content, lang):
    c = rewrite_zone_links(content, lang)

    # 1. Frontmatter description
    # e.g.: description: "PvP open-terraformable zone: 7 ore types, 17 plant species, 2048×2048 tiles."
    # e.g.: description: "PvE protected zone: 5 ore types, 19 plant species, 2048×2048 tiles."
    # e.g.: description: "PvP open zone: no plant rules, 256×256 tiles."
    desc_m = re.search(r'description:\s*"([^"]+)"', c)
    if desc_m:
        orig_desc = desc_m.group(1)
        type_word = (t(lang, "zones", "type_pvp") if "PvP" in orig_desc
                     else (t(lang, "zones", "type_pve") if "PvE" in orig_desc
                     else (t(lang, "zones", "type_training") if "Training" in orig_desc else "")))
        prot_word = "protected" if "protected" in orig_desc else ("open-terraformable" if "open-terraformable" in orig_desc else ("open" if "open" in orig_desc else ""))
        ore_m = re.search(r'(\d+)\s+ore types?', orig_desc)
        ore_cnt = f"{ore_m.group(1)} {t(lang, 'zones', 'desc_ore_types')}, " if ore_m else ""
        plant_m = re.search(r'(\d+)\s+plant species', orig_desc)
        plant_cnt = f"{plant_m.group(1)} {t(lang, 'zones', 'desc_plant_species')}" if plant_m else ("no plant rules" if "no plant rules" in orig_desc else "")
        if plant_cnt == "no plant rules":
            plant_cnt = t(lang, "zones", "no_plant_rules")
        size_m = re.search(r'(\d+[×x]\d+)\s+tiles', orig_desc)
        size_part = f", {size_m.group(1)} {t(lang, 'zones', 'tiles')}." if size_m else "."
        prot_tr = t(lang, "zones", PROT_KEYS[prot_word])

        # Localized description
        if lang in ["zh-CN", "zh-TW"]:
            new_desc = f"{type_word} {prot_tr}{t(lang, 'zones', 'zone')}：{ore_cnt}{plant_cnt}{size_part}"
        elif lang in ["ja", "ko"]:
            new_desc = f"{type_word} {prot_tr} {t(lang, 'zones', 'zone')}: {ore_cnt}{plant_cnt}{size_part}"
        else:
            new_desc = f"{t(lang, 'zones', 'zone').capitalize()} {type_word} {prot_tr}: {ore_cnt}{plant_cnt}{size_part}"
        c = c.replace(f'description: "{orig_desc}"', f'description: "{new_desc}"')

    # 2. Worldmap card
    c = c.replace("<strong>World map</strong> — where this zone sits among all the others, with the teleport connections. Open the full map.",
                  f"<strong>{t(lang, 'zones', 'world_map')}</strong> — {t(lang, 'zones', 'worldmap_card_desc')}")

    # 3. Teleport image alt
    tele_prefix = t(lang, "zones", "teleport_columns_in")
    if lang in ["ja", "ko"]:
        c = re.sub(r'!\[Teleport columns in ([^\]]+)\]', rf'![\1{tele_prefix}]', c)
    else:
        c = re.sub(r'!\[Teleport columns in ([^\]]+)\]', rf'![{tele_prefix} \1]', c)

    # 4. Map caption
    has_local = "The dashed lines connect the pairs of local" in c
    caption_txt = t(lang, "zones", "map_caption_main") + (t(lang, "zones", "map_caption_local") if has_local else "")
    c = re.sub(r'Where this zone\'s teleport columns stand \(dots.*?\.\n', caption_txt + "\n", c, flags=re.DOTALL)

    # 5. Intro paragraph
    # Match paragraph between caption and facts table:
    intro_m = re.search(r'(\n\n)([^\n|#]+)(\n\n\|\s*Fact)', c)
    if intro_m:
        orig_intro = intro_m.group(2).strip()
        trans_intro = translate_intro(orig_intro, lang)
        c = c.replace(orig_intro, trans_intro)

    # 6. Facts table headers & row keys
    c = c.replace("| Fact | Value |", f"| {t(lang, 'zones', 'fact')} | {t(lang, 'zones', 'value')} |")
    for fact_key in [
        ("Zone id", "zone_id"), ("Type", "type"), ("Protection", "protection"),
        ("Size", "size"), ("Tier", "tier"), ("Fertility", "fertility"),
        ("Plant species", "plant_species"), ("Ore types", "ore_types"),
        ("Total ore nodes", "total_ore_nodes"), ("Round time limit", "round_time_limit"),
        ("PBS tech limit", "pbs_tech_limit"), ("Max docking bases", "max_docking_bases"),
    ]:
        c = re.sub(rf'^\|\s*{re.escape(fact_key[0])}\s*\|', f"| {t(lang, 'zones', fact_key[1])} |", c, flags=re.MULTILINE)

    # Facts table values
    c = c.replace("— protected, PvP disabled", f"— {t(lang, 'zones', 'prot_alpha_desc')}")
    c = c.replace("— open PvP, standard terrain", f"— {t(lang, 'zones', 'prot_beta_desc')}")
    c = c.replace("— open PvP, terraformable", f"— {t(lang, 'zones', 'prot_gamma_desc')}")
    c = re.sub(r'(\d+[×x]\d+)\s+tiles', rf'\1 {t(lang, "zones", "tiles")}', c)
    c = c.replace("(server-recorded)", t(lang, "zones", "server_recorded"))
    c = re.sub(r'\(rule set (\d+)\)', rf'({t(lang, "zones", "rule_set")} \1)', c)
    c = c.replace("– (no ruleset)", t(lang, "zones", "no_ruleset"))
    c = re.sub(r'\|\s*none\s*\|', f"| {t(lang, 'zones', 'none')} |", c)

    # 7. Ore configuration section
    c = c.replace("## Ore configuration", f"## {t(lang, 'zones', 'ore_configuration')}")
    ores_link = f"/{lang}/content/ores/"
    ore_desc = t(lang, "zones", "ore_config_p").replace("{ores_link}", ores_link)
    c = re.sub(r'The node generation this zone maintains\..*?\n\n', ore_desc + "\n\n", c)

    # Table headers
    c = c.replace("| Material | Nodes | Max tiles/node | Total per node | Min threshold |",
                  f"| {t(lang, 'zones', 'material')} | {t(lang, 'zones', 'nodes')} | {t(lang, 'zones', 'max_tiles_per_node')} | {t(lang, 'zones', 'total_per_node')} | {t(lang, 'zones', 'min_threshold')} |")

    # Pie chart title
    c = c.replace("title Steady-state ore stock by type (million units)",
                  f"title {t(lang, 'zones', 'pie_title')}")

    # 8. Bottom links
    # [Zone index](/zones/zone-index/) · [World map](/zones/map/#...) · [Protection levels](/zones/protection/)
    zone_idx_tr = t(lang, "zones", "zone_index")
    world_map_tr = t(lang, "zones", "world_map")
    prot_levels_tr = t(lang, "zones", "protection_levels")
    c = re.sub(r'\[Zone index\]\(/[^)]+/zones/zone-index/\)', f'[{zone_idx_tr}](/{lang}/zones/zone-index/)', c)
    c = re.sub(r'\[World map\]\(/[^)]+/zones/map/([^)]*)\)', rf'[{world_map_tr}](/{lang}/zones/map/\1)', c)
    c = re.sub(r'\[Protection levels\]\(/[^)]+/zones/protection/\)', f'[{prot_levels_tr}](/{lang}/zones/protection/)', c)

    return c


def build_protection_page(lang):
    """Build zones/protection.md from the translations/<lang>.json prose."""
    title = t(lang, "zones", "pages", "protection", "title")
    desc = t(lang, "zones", "pages", "protection", "description")
    body = t(lang, "zones", "pages", "protection", "body")
    md = f"---\ntitle: \"{title}\"\ndescription: \"{desc}\"\nweight: 20\n---\n\n{body}\n"
    return rewrite_links(md, lang)


def build_zones_index_page(lang):
    """Build zones/_index.md from the translations/<lang>.json prose."""
    title = t(lang, "zones", "pages", "index", "title")
    desc = t(lang, "zones", "pages", "index", "description")
    body = t(lang, "zones", "pages", "index", "body")
    md = f"---\ntitle: \"{title}\"\ndescription: \"{desc}\"\nweight: 50\n---\n\n{body}\n"
    return rewrite_links(md, lang)


def process_alpha_overview(content, lang):
    c = rewrite_zone_links(content, lang)
    c = re.sub(r'description:\s*"[^"]*"', f'description: "{t(lang, "zones", "alpha_desc")}"', c)
    desc_intro = t(lang, "zones", "alpha_intro").replace("{lang}", lang)
    c = re.sub(r'The main protected islands and their second-wave PvE companions.*?\n', desc_intro + "\n", c)
    c = re.sub(r'\[World map\]\(/[^)]+/zones/map/\)', f'[{t(lang, "zones", "world_map")}](/{lang}/zones/map/)', c)
    c = re.sub(r'\[Zone index\]\(/[^)]+/zones/zone-index/\)', f'[{t(lang, "zones", "zone_index")}](/{lang}/zones/zone-index/)', c)
    c = re.sub(r'\[Protection levels\]\(/[^)]+/zones/protection/\)', f'[{t(lang, "zones", "protection_levels")}](/{lang}/zones/protection/)', c)
    return c


def process_beta_overview(content, lang):
    c = rewrite_zone_links(content, lang)
    c = re.sub(r'description:\s*"[^"]*"', f'description: "{t(lang, "zones", "beta_desc")}"', c)
    desc_intro = t(lang, "zones", "beta_intro").replace("{lang}", lang)
    c = re.sub(r"The open-PvP islands: the three main islands' PvP twins.*?\n", desc_intro + "\n", c)
    c = re.sub(r'\[World map\]\(/[^)]+/zones/map/\)', f'[{t(lang, "zones", "world_map")}](/{lang}/zones/map/)', c)
    c = re.sub(r'\[Zone index\]\(/[^)]+/zones/zone-index/\)', f'[{t(lang, "zones", "zone_index")}](/{lang}/zones/zone-index/)', c)
    c = re.sub(r'\[Protection levels\]\(/[^)]+/zones/protection/\)', f'[{t(lang, "zones", "protection_levels")}](/{lang}/zones/protection/)', c)
    return c


def process_gamma_overview(content, lang):
    c = rewrite_zone_links(content, lang)
    c = re.sub(r'description:\s*"[^"]*"', f'description: "{t(lang, "zones", "gamma_desc")}"', c)

    # Intro paragraph (Protection-levels link captured)
    c = re.sub(
        r'The frontier belt, split by the server-recorded tier \(zones\.note\): the six tc transit zones \(T0\) and the tier islands T1–T4 — open PvP and terraformable, see (\[Protection levels\]\([^)]+\))\.',
        lambda m: t(lang, "zones", "gamma_intro").replace("{protection_link}", m.group(1)), c
    )

    # Per-tier island intros (T1..T4)
    def _repl_island(m):
        tier, prot = m.group(1), m.group(2)
        return t(lang, "zones", "gamma_island_intro").replace("{tier}", tier).replace("{protection_link}", prot)

    c = re.sub(
        r'Frontier belt islands with the server-recorded tier \*\*(T\d)\*\* \(zones\.note\)\. Open PvP and terraformable — see (\[Protection levels\]\([^)]+\))\. Each island.s page has its ore configuration and TP connections\.',
        _repl_island, c
    )

    c = c.replace("## Gamma T0 — tc transit", f"## {t(lang, 'zones', 'gamma_t0')}")
    c = c.replace(
        "The six small (256-tile) transit zones of the frontier belt. No ore configuration — pure travel nodes between the main galaxies and the belt.",
        t(lang, "zones", "gamma_tc_desc")
    )
    c = re.sub(r'\[World map\]\(/[^)]+/zones/map/\)', f'[{t(lang, "zones", "world_map")}](/{lang}/zones/map/)', c)
    c = re.sub(r'\[Zone index\]\(/[^)]+/zones/zone-index/\)', f'[{t(lang, "zones", "zone_index")}](/{lang}/zones/zone-index/)', c)
    c = re.sub(r'\[Protection levels\]\(/[^)]+/zones/protection/\)', f'[{t(lang, "zones", "protection_levels")}](/{lang}/zones/protection/)', c)
    return c


def process_zone_index_overview(content, lang):
    c = rewrite_zone_links(content, lang)
    c = re.sub(r'description:\s*"[^"]*"', f'description: "{t(lang, "zones", "zone_index_desc")}"', c)
    c = re.sub(r'title:\s*"Zone index"', f'title: "{t(lang, "zones", "zone_index")}"', c)
    c = re.sub(r'^#\s*Zone index', f'# {t(lang, "zones", "zone_index")}', c, flags=re.MULTILINE)

    # Intro paragraph (count + world-map + family links captured)
    c = re.sub(
        r'All (\d+) zones that have at least one teleport point to ANOTHER zone, grouped by family \(the same grouping as the (\[world map\]\([^)]+\))\) — the card links to the zone.s page\. Zones without any inter-zone teleport point \(the strongholds, the PvP arena, dead-end gate islands\) are left off; they are still reachable from the world map.s gate lines\. The per-family pages — (\[Alpha\]\([^)]+\)) · (\[Beta\]\([^)]+\)) · (\[Gamma\]\([^)]+\)) — list every zone of the family regardless of TPs\.',
        lambda m: (t(lang, "zones", "zone_index_intro")
                   .replace("{count}", m.group(1))
                   .replace("{map_link}", m.group(2))
                   .replace("{alpha_link}", m.group(3))
                   .replace("{beta_link}", m.group(4))
                   .replace("{gamma_link}", m.group(5))), c
    )

    # Family section intros
    c = re.sub(
        r'The virtual (\[training island\]\([^)]+\)) — where new characters start and learn the basics before entering the main galaxies\.',
        lambda m: t(lang, "zones", "zone_index_training").replace("{training_link}", m.group(1)), c
    )
    c = re.sub(
        r'The main protected islands and their second-wave PvE companions — the safe starter economy \(see (\[Protection levels\]\([^)]+\))\)\.',
        lambda m: t(lang, "zones", "zone_index_alpha").replace("{protection_link}", m.group(1)), c
    )
    c = re.sub(
        r'The open-PvP islands: the three main islands.\s+PvP twins \(the "_real" names\), the eight gate islands of each galaxy, and the special zones \(the (\[PvP arena\]\([^)]+\)) and the strongholds — protected instances, listed here for completeness\)\.',
        lambda m: t(lang, "zones", "zone_index_beta").replace("{arena_link}", m.group(1)), c
    )

    c = re.sub(r'\[World map\]\(/[^)]+/zones/map/\)', f'[{t(lang, "zones", "world_map")}](/{lang}/zones/map/)', c)
    c = re.sub(r'\[Protection levels\]\(/[^)]+/zones/protection/\)', f'[{t(lang, "zones", "protection_levels")}](/{lang}/zones/protection/)', c)
    return c


def process_map_overview(content, lang):
    c = rewrite_zone_links(content, lang)
    world_tr = t(lang, "zones", "world")
    c = re.sub(r'description:\s*"[^"]*"', f'description: "{t(lang, "zones", "map_desc")}"', c)
    c = re.sub(r'title:\s*"World"', f'title: "{world_tr}"', c)
    c = re.sub(r'^#\s*World', f'# {world_tr}', c, flags=re.MULTILINE)

    # "Zone listings:" line. Alpha/Beta/Gamma are proper nouns (stay
    # English, so the captured links are reused as-is); the Zone index and
    # Protection levels links are REBUILT with translated labels — capturing
    # them verbatim would leave the English link text in every language.
    c = re.sub(
        r'Zone listings: (\[Alpha\]\([^)]+\)) · (\[Beta\]\([^)]+\)) · (\[Gamma\]\([^)]+\)) — \[Zone index\]\(([^)]+)\) · \[Protection levels\]\(([^)]+)\)',
        lambda m: (t(lang, "zones", "map_listings")
                   .replace("{alpha_link}", m.group(1))
                   .replace("{beta_link}", m.group(2))
                   .replace("{gamma_link}", m.group(3))
                   .replace("{index_link}", f"[{t(lang, 'zones', 'zone_index')}]({m.group(4)})")
                   .replace("{protection_link}", f"[{t(lang, 'zones', 'protection_levels')}]({m.group(5)})")), c
    )

    M = lambda key: t(lang, "zones", key)

    # Zoom-reset button title + SVG accessible name/title
    c = c.replace('title="Reset the zoom"', f'title="{M("map_reset_zoom")}"')
    c = c.replace(
        'aria-label="Map of all game zones with teleport connections, at their grid positions, coastline outlines colored by galaxy family"',
        f'aria-label="{M("map_aria")}"'
    )
    c = c.replace(
        '<title>Map of all game zones with teleport connections, at their grid positions</title>',
        f'<title>{M("map_svg_title")}</title>'
    )

    # Node tooltips: "— open (family)" / "— protected (family)" / "— Base"
    # (family names and the · Type part are in-game terms, stay English)
    c = c.replace(" — open (", f" — {M('tip_open')} (")
    c = c.replace(" — protected (", f" — {M('tip_protected')} (")
    c = c.replace(" — Base</title>", f" — {M('legend_base')}</title>")

    # Legend toggle + group heads
    c = c.replace('aria-expanded="false">Legend</button>',
                  f'aria-expanded="false">{M("map_legend")}</button>')

    # Stable data-group attribute on the Landmarks group (the inline script
    # uses it instead of matching the translated heading text)
    c = re.sub(
        r'<div class="map-legend-group">\s*<button type="button" class="map-legend-head" aria-expanded="true">Landmarks</button>',
        '<div class="map-legend-group" data-group="landmarks">\n    '
        '<button type="button" class="map-legend-head" aria-expanded="true">Landmarks</button>',
        c
    )
    # Stable data-galaxy attributes on the galaxy legend items
    for color, gal in [("#41d3ff", "tm"), ("#6ee7a0", "ics"), ("#f5a05a", "asi")]:
        c = c.replace(
            f'<li><span class="legend-swatch" style="background:{color}"></span>',
            f'<li data-galaxy="{gal}"><span class="legend-swatch" style="background:{color}"></span>'
        )
    for en_head, key in [("Protection", "legend_protection"), ("Galaxies", "legend_galaxies"),
                         ("Landmarks", "legend_landmarks")]:
        c = c.replace(f'map-legend-head" aria-expanded="true">{en_head}</button>',
                      f'map-legend-head" aria-expanded="true">{M(key)}</button>')
    for en_item, key in [("Alpha (PvE)", "legend_alpha"), ("Beta (PvP)", "legend_beta"),
                         ("Gamma (PvP + Terraforming)", "legend_gamma"),
                         ("Labels", "legend_labels"), ("Base", "legend_base"),
                         ("Field terminal", "legend_field_terminal"),
                         ("Teleport", "legend_teleport"),
                         ("Teleport path", "legend_teleport_path"),
                         ("Gamma gateway teleport", "legend_gateway_tp")]:
        c = c.replace(f'</span>{en_item}</li>', f'</span>{M(key)}</li>')
    # (Galaxy items "TM (The Matriarkh)" etc. are proper nouns — left English.)

    # Island-sizes legend line (numbers are data; training/stronghold are
    # in-game terms, so only the main-islands and tc-zones labels are keys)
    c = c.replace("Island sizes (tiles):", M("island_sizes_label"))
    for size, en_label, key in [("2048", "main islands", "island_main"),
                                ("1024", "training", None),
                                ("512", "stronghold", None),
                                ("256", "tc zones", "island_tc")]:
        label = M(key) if key else en_label
        c = c.replace(f"{size} ({en_label})",
                      M("island_size").replace("{size}", size).replace("{label}", label))

    # Inline legend script: match on stable tokens instead of translated text
    c = c.replace("if (group === 'Landmarks') return;",
                  "if (li.closest('.map-legend-group').getAttribute('data-group') === 'landmarks') return;")
    c = c.replace("titleIncludes = 'protected (alpha)';", "titleIncludes = '(alpha)';")
    c = c.replace("titleIncludes = 'open (beta)';", "titleIncludes = '(beta)';")
    c = c.replace("else if (text.includes('Gamma (PvP')) titleIncludes = 'open (gamma)';",
                  "else if (text.includes('Gamma')) titleIncludes = '(gamma)';")
    c = c.replace(
        "else if (text.includes('TM (The')) selector = '.zonemap-node-tm'; "
        "else if (text.includes('ICS (Inter')) selector = '.zonemap-node-ics'; "
        "else if (text.includes('ASI (Asce')) selector = '.zonemap-node-asi'; "
        "else if (text.includes('Gamma') && !text.includes('gateway')) selector = '.zonemap-node-gamma'; "
        "else return;",
        "else if (li.getAttribute('data-galaxy')) selector = '.zonemap-node-' + li.getAttribute('data-galaxy'); else return;"
    )
    return c


def main():
    root = Path(".")
    src_zones_dir = root / "content" / "zones"

    if not src_zones_dir.exists():
        print(f"gen_zone_translations: source directory {src_zones_dir} not found!", file=sys.stderr)
        sys.exit(1)

    t0 = time.time()
    generated_count = 0

    HANDWRITTEN_PROSE = {
        "generation.md",
        "zone_tm.md", "zone_asi.md", "zone_gamma_z106.md"
    }

    all_zone_files = sorted(src_zones_dir.glob("*.md"))

    for lang in LANGUAGES:
        dest_dir = root / "content" / lang / "zones"
        dest_dir.mkdir(parents=True, exist_ok=True)

        for src_file in all_zone_files:
            fname = src_file.name

            # Skip the rich hand-written prose pages (managed by translators)
            if fname in HANDWRITTEN_PROSE:
                continue

            # The protection-levels page and the zone index are rendered from
            # the translations/<lang>.json prose (zones.pages.*)
            if fname == "_index.md":
                out_content = build_zones_index_page(lang)
            elif fname == "protection.md":
                out_content = build_protection_page(lang)
            else:
                content = src_file.read_text(encoding="utf-8")
                if fname == "alpha.md":
                    out_content = process_alpha_overview(content, lang)
                elif fname == "beta.md":
                    out_content = process_beta_overview(content, lang)
                elif fname == "gamma.md":
                    out_content = process_gamma_overview(content, lang)
                elif fname == "zone-index.md":
                    out_content = process_zone_index_overview(content, lang)
                elif fname == "map.md":
                    out_content = process_map_overview(content, lang)
                else:
                    out_content = process_generated_zone_page(content, lang)

            dest_path = dest_dir / fname
            dest_path.write_text(out_content, encoding="utf-8")
            generated_count += 1

    dt = time.time() - t0
    print(f"gen_zone_translations: wrote {generated_count} localized zone files across {len(LANGUAGES)} languages in {dt:.2f}s")


if __name__ == "__main__":
    main()
