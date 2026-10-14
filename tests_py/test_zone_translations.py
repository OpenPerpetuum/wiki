"""tools/gen_zone_translations.py — zone pages + world map transformations."""
import gen_zone_translations as gzt
from i18n_common import t

LANG = "fr"

ZONE_FIXTURE = '''---
title: "Shinjalar (zone_ASI_pve)"
description: "PvE protected zone: 5 ore types, 14 plant species, 2048×2048 tiles."
---

# Shinjalar (zone_ASI_pve)

<div class="worldmap-card">
  <a href="/zones/map/">
    <img src="/world-map-thumb.png" alt="" loading="lazy">
    <span class="worldmap-card-body"><strong>World map</strong> — where this zone sits among all the others, with the teleport connections. Open the full map.</span>
  </a>
</div>

![Teleport columns in Shinjalar (zone_ASI_pve)](/zonemaps/zone-asi-pve.svg)

Where this zone's teleport columns stand (dots, labelled with the destination — dimmed where the column is currently switched off), the landing spots of teleports arriving from other zones (dashed circles), and the exit gates (diamonds) where one exists. Positions are the tile coordinates the server records. The dashed lines connect the pairs of local (in-zone) teleport columns.

A protected (Alpha) Daoden (ASI) zone — safe from player attack, the standard gathering ground for the Daoden (ASI) galaxy. It maintains 5 ore types.

| Fact | Value |
|---|---|
| Zone id | 7 |
| Type | PvE |
| Protection | [Alpha](/zones/protection/) — protected, PvP disabled |
| Size | 2048×2048 tiles |
| Plant species | 14 (rule set 7) |
| Max docking bases | none |

## Ore configuration

The node generation this zone maintains. Per-ore yields and the generation formulas are in [Ores](/content/ores/) (this zone's section is linked below).

| Material | Nodes | Max tiles/node | Total per node | Min threshold |
|---|---|---|---|---|
| [titan](/content/ores/titan/) | 7 | 625 | 80M | 0.5 |

```mermaid
pie showData
    title Steady-state ore stock by type (million units)
    "titan" : 560
```

[Zone index](/zones/zone-index/) · [World map](/zones/map/#alpha) · [Protection levels](/zones/protection/)
'''

MAP_FIXTURE = '''---
title: "World map"
---

<svg class="zonemap">
<title>Map of all game zones with teleport connections, at their grid positions</title>
<a><circle cx="1" cy="1" r="2" class="zonemap-node-alpha"><title>zone_alpha — protected (alpha) · Main island (2048 / 2048)</title></circle></a>
<a><circle cx="2" cy="2" r="2" class="zonemap-node-beta"><title>zone_beta — open (beta) · PvP island (2048 / 2048)</title></circle></a>
<a><circle cx="3" cy="3" r="2" class="zonemap-node-gamma"><title>Gamma TC Z100 — Base</title></circle></a>
</svg>
<button type="button" class="map-legend-toggle" id="map-legend-toggle" aria-expanded="false">Legend</button>
<div class="map-legend legend-hidden" id="map-legend">
  <div class="map-legend-group">
    <button type="button" class="map-legend-head" aria-expanded="true">Protection</button>
    <ul class="map-legend-items">
      <li><span class="legend-swatch" style="background:transparent;border:2px solid #41d3ff"></span>Alpha (PvE)</li>
      <li><span class="legend-swatch" style="background:transparent;border:2px solid #fbbf24"></span>Beta (PvP)</li>
      <li><span class="legend-swatch" style="background:transparent;border:2px solid #ef4444"></span>Gamma (PvP + Terraforming)</li>
    </ul>
  </div>
  <div class="map-legend-group">
    <button type="button" class="map-legend-head" aria-expanded="true">Galaxies</button>
    <ul class="map-legend-items">
      <li><span class="legend-swatch" style="background:#41d3ff"></span>TM (The Matriarkh)</li>
      <li><span class="legend-swatch" style="background:#6ee7a0"></span>ICS (Interstellar Coalition)</li>
      <li><span class="legend-swatch" style="background:#f5a05a"></span>ASI (Ascension)</li>
    </ul>
  </div>
  <div class="map-legend-group">
    <button type="button" class="map-legend-head" aria-expanded="true">Landmarks</button>
    <ul class="map-legend-items">
      <li><span class="legend-icon">Aa</span>Labels</li>
      <li><span class="legend-icon">◉</span>Base</li>
      <li><span class="legend-icon">▽</span>Field terminal</li>
      <li><span class="legend-icon">⬡</span>Teleport</li>
      <li><span class="legend-icon">╌</span>Teleport path</li>
      <li><span class="legend-icon" style="color:#a78bfa">◉</span>Gamma gateway teleport</li>
    </ul>
  </div>
</div>
<script>var g=1; if (group === 'Landmarks') return; var titleIncludes = ''; var selector = ''; if (text.includes('Alpha')) titleIncludes = 'protected (alpha)'; else if (text.includes('Beta')) titleIncludes = 'open (beta)'; else if (text.includes('Gamma (PvP')) titleIncludes = 'open (gamma)'; else if (text.includes('TM (The')) selector = '.zonemap-node-tm'; else if (text.includes('ICS (Inter')) selector = '.zonemap-node-ics'; else if (text.includes('ASI (Asce')) selector = '.zonemap-node-asi'; else if (text.includes('Gamma') && !text.includes('gateway')) selector = '.zonemap-node-gamma'; else return; </script></div>

<div class="zonemap-legend">Island sizes (tiles): <span class="legend-isle" style="width:19px;min-width:6px"></span> 2048 (main islands);&ensp; <span class="legend-isle" style="width:12px;min-width:6px"></span> 1024 (training);&ensp; <span class="legend-isle" style="width:7.5px;min-width:6px"></span> 512 (stronghold);&ensp; <span class="legend-isle" style="width:5px;min-width:6px"></span> 256 (tc zones);&ensp; </div>

Zone listings: [Alpha](/zones/alpha/) · [Beta](/zones/beta/) · [Gamma](/zones/gamma/) — [Zone index](/zones/zone-index/) · [Protection levels](/zones/protection/)
'''


# ---------------------------------------------------------- zone pages

def test_zone_description_localized():
    out = gzt.process_generated_zone_page(ZONE_FIXTURE, LANG)
    # "PvE protected zone: 5 ore types, 14 plant species, 2048×2048 tiles."
    # → "{Zone} {type} {protection}: {n} {ore_types}, {n} {plant_species}, {size} {tiles}."
    expected = (f"{t(LANG, 'zones', 'zone').capitalize()} "
                f"{t(LANG, 'zones', 'type_pve')} {t(LANG, 'zones', 'protected')}: "
                f"5 {t(LANG, 'zones', 'desc_ore_types')}, "
                f"14 {t(LANG, 'zones', 'desc_plant_species')}, "
                f"2048×2048 {t(LANG, 'zones', 'tiles')}.")
    assert f'description: "{expected}"' in out
    assert "PvE protected zone: 5 ore types" not in out


def test_zone_page_sections_localized():
    out = gzt.process_generated_zone_page(ZONE_FIXTURE, LANG)
    # worldmap card
    assert f"<strong>{t(LANG, 'zones', 'world_map')}</strong>" in out
    # image alt
    assert f"![{t(LANG, 'zones', 'teleport_columns_in')} Shinjalar (zone_ASI_pve)]" in out
    # caption (main + local parts)
    assert t(LANG, "zones", "map_caption_main") in out
    assert t(LANG, "zones", "map_caption_local") in out
    # facts table
    assert f"| {t(LANG, 'zones', 'fact')} | {t(LANG, 'zones', 'value')} |" in out
    assert f"| {t(LANG, 'zones', 'zone_id')} | 7 |" in out
    assert f"— {t(LANG, 'zones', 'prot_alpha_desc')}" in out
    assert f"2048×2048 {t(LANG, 'zones', 'tiles')}" in out
    assert f"({t(LANG, 'zones', 'rule_set')} 7)" in out
    assert f"| {t(LANG, 'zones', 'none')} |" in out
    # ore configuration + pie title
    assert f"## {t(LANG, 'zones', 'ore_configuration')}" in out
    assert f"title {t(LANG, 'zones', 'pie_title')}" in out
    # bottom links carry the language prefix, anchors preserved
    assert f"[{t(LANG, 'zones', 'world_map')}](/{LANG}/zones/map/#alpha)" in out
    assert f"[{t(LANG, 'zones', 'protection_levels')}](/{LANG}/zones/protection/)" in out


def test_zone_intro_alpha_protected():
    out = gzt.process_generated_zone_page(ZONE_FIXTURE, LANG)
    intro = t(LANG, "zones", "intro", "alpha_protected").replace("{fam}", "Daoden (ASI)")
    assert intro in out
    assert "A protected (Alpha) Daoden (ASI) zone" not in out
    # "It maintains 5 ore types." is appended in translation
    assert t(LANG, "zones", "maintains_ore_types").replace("{n}", "5") in out


def test_zone_intro_beta_and_gamma():
    # the intro paragraph is only located when it sits above the facts table
    facts = "\n\n| Fact | Value |\n| --- | --- |\n"
    beta = 'An open-PvP (beta) Daoden (ASI) island — players can attack freely and blobs apply.'
    out = gzt.process_generated_zone_page(f"\n\n{beta}{facts}", LANG)
    assert t(LANG, "zones", "intro", "beta_open").replace("{fam}", "Daoden (ASI)") in out
    gamma = 'An open-PvP, terraformable (gamma) X island — the ground can be reshaped by players.'
    out = gzt.process_generated_zone_page(f"\n\n{gamma}{facts}", LANG)
    assert t(LANG, "zones", "intro", "gamma_terraformable").replace("{fam}", "X") in out


# ------------------------------------------------------------- world map

def test_map_legend_groups_and_items_localized():
    out = gzt.process_map_overview(MAP_FIXTURE, LANG)
    # group heads
    for key in ("legend_protection", "legend_galaxies", "legend_landmarks"):
        assert f'aria-expanded="true">{t(LANG, "zones", key)}</button>' in out, key
    # protection + landmark items
    for key in ("legend_alpha", "legend_beta", "legend_gamma",
                "legend_labels", "legend_base", "legend_field_terminal",
                "legend_teleport", "legend_teleport_path", "legend_gateway_tp"):
        assert f"</span>{t(LANG, 'zones', key)}</li>" in out, key
    # proper-noun galaxy items stay English
    assert "TM (The Matriarkh)" in out
    assert "ICS (Interstellar Coalition)" in out
    assert "ASI (Ascension)" in out


def test_map_stable_attributes_for_click_to_zoom():
    out = gzt.process_map_overview(MAP_FIXTURE, LANG)
    # the Landmarks group gets a data-group attribute (script uses it)
    assert 'data-group="landmarks"' in out
    # galaxy items get data-galaxy attributes
    for color, gal in [("#41d3ff", "tm"), ("#6ee7a0", "ics"), ("#f5a05a", "asi")]:
        assert f'<li data-galaxy="{gal}"><span class="legend-swatch" style="background:{color}"></span>' in out
    # the inline script no longer matches on translated text
    assert "if (group === 'Landmarks') return;" not in out
    assert "getAttribute('data-group') === 'landmarks'" in out
    assert "titleIncludes = '(alpha)'" in out
    assert "titleIncludes = '(beta)'" in out
    assert "titleIncludes = '(gamma)'" in out
    assert "li.getAttribute('data-galaxy')" in out
    assert "text.includes('TM (The')" not in out


def test_map_tooltips_and_chrome():
    out = gzt.process_map_overview(MAP_FIXTURE, LANG)
    assert f" — {t(LANG, 'zones', 'tip_open')} (" in out
    assert f" — {t(LANG, 'zones', 'tip_protected')} (" in out
    assert f" — {t(LANG, 'zones', 'legend_base')}</title>" in out
    assert f">{t(LANG, 'zones', 'map_legend')}</button>" in out
    assert f"<title>{t(LANG, 'zones', 'map_svg_title')}</title>" in out
    # zone slugs + in-game family/type words stay English
    assert "zone_alpha — " in out
    assert "(alpha) · Main island" in out


def test_map_island_sizes_and_listings():
    out = gzt.process_map_overview(MAP_FIXTURE, LANG)
    assert t(LANG, "zones", "island_sizes_label") in out
    # main islands + tc zones translated; training/stronghold stay English
    tmpl = t(LANG, "zones", "island_size")
    assert tmpl.replace("{size}", "2048").replace("{label}", t(LANG, "zones", "island_main")) in out
    assert tmpl.replace("{size}", "256").replace("{label}", t(LANG, "zones", "island_tc")) in out
    assert "1024 (training)" in out
    assert "512 (stronghold)" in out
    # zone listings line: all five labels translated, links localized
    assert f"[{t(LANG, 'zones', 'zone_index')}](/{LANG}/zones/zone-index/)" in out
    assert "Zone listings: [Alpha](/zones/alpha/)" not in out
