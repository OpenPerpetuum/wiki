"""tools/gen_content_translations.py — the process_* page transformers.

Fixtures are trimmed copies of the real generated pages; expected values are
computed through i18n_common.t() so the tests assert *behavior* (the French
string lands in the page), not hardcoded words.
"""
import gen_content_translations as gct
import i18n_common
from i18n_common import t

LANG = "fr"

ROBOT_FIXTURE = '''---
title: "Arbalest"
description: "Arbalest — robot stats, production and availability."
---

# Arbalest

<li><b>»»»</b><span>Combat</span></li>
<li><b>»»»</b><span>Speed</span></li>
<li><b>■■■</b><span>Armor</span></li>
<li><b>□□</b><span>Storage</span></li>
<li><b>$$$</b><span>Cost</span></li>

<tr><td>Class</td><td>Standard</td></tr>
<tr><td>Size</td><td>12</td></tr>
<tr><td>Mass</td><td>0</td></tr>
<tr><td>Health</td><td>100</td></tr>
<tr><td>Purchasable</td><td>Yes</td></tr>

## Variants

| Variant | Link |
|---|---|
| Arbalest Mk2 | [/arbalest-mk2/](/content/robots/arbalest-mk2/) |

## Production

Components required to build this robot:

| Component | Amount |
|---|---|
| [Titanium](/content/items/titanium/) | 1,000 |
'''

NODE_FIXTURE = '''---
title: "Braviar ECCM — tech tree node"
description: "Research node that unlocks Braviar ECCM (Common (second set) category)."
---

# Braviar ECCM (research node)

This node of the [Common (second set)](/content/techtree/groups/common2/) research tree unlocks [Braviar ECCM](/content/items/named3-eccm/).

|  |  |
|---|---|
| Category | [Common (second set)](/content/techtree/groups/common2/) |
| Unlocks | [Braviar ECCM](/content/items/named3-eccm/) |
| Parent node | [Deshrud-QW ECCM](/content/techtree/nodes/named2-eccm/) |
| Unlocks next | – (end of line) |
| Point prices | common=12.5k; hitech=6.25k |

[All tech tree nodes](/content/techtree/)
'''

# The real MSD m\\2315 'Filch' node: a backslash in the frontmatter title is
# what broke re.sub's template unescaping (regression: the lambda fix).
NODE_BACKSLASH_FIXTURE = '''---
title: "MSD m\\2315 'Filch' sensor suppressor — tech tree node"
description: "Research node that unlocks MSD m\\2315 'Filch' sensor suppressor (Thelodica (faction) category)."
---

# MSD m\\2315 'Filch' sensor suppressor (research node)

This node of the [Thelodica (faction)](/content/techtree/groups/thelodica/) research tree unlocks [MSD m\\2315 'Filch' sensor suppressor](/content/items/named2-sensor-dampener/).
'''

PLANTS_DIAGRAM_FIXTURE = '''---
title: "Plants"
description: "d"
---

# Plants

```mermaid
flowchart TD
    S["Sprout (stage 1)"] --> G["Grow: growRate cycles per stage"]
    G --> F["Fruiting stage reached"]
    F --> H["Harvestable: fruit x fruitAmount"]
    H --> K["Killed / damaged"]
    K --> R["Zone respawns toward the\\nfertility target (weighted by species fertility)"]
    R --> S
```
'''


# ---------------------------------------------------------------- robot

def test_robot_stats_and_props_translated():
    out = gct.process_robot_file(ROBOT_FIXTURE, LANG)
    for stat in ("combat", "speed", "armor", "storage", "cost"):
        assert f"<span>{t(LANG, 'labels', stat)}</span>" in out
    # (no "absent English label" assertion for stats: several labels are
    # identical in EN and FR, e.g. combat → Combat)
    for prop in ("class", "size", "mass", "health", "purchasable"):
        assert f"<td>{t(LANG, 'labels', prop)}</td>" in out
    assert f"<td>{t(LANG, 'labels', 'yes')}</td>" in out


def test_robot_sections_and_links():
    out = gct.process_robot_file(ROBOT_FIXTURE, LANG)
    assert f"## {t(LANG, 'robots', 'variants')}" in out
    assert f"## {t(LANG, 'robots', 'production')}" in out
    assert t(LANG, "robots", "components_required") in out
    # /content/robots/ links are localized; /content/items/ stay global
    assert f"(/{LANG}/content/robots/arbalest-mk2/)" in out
    assert "(/content/items/titanium/)" in out


# -------------------------------------------------------- techtree nodes

def test_techtree_node_translation():
    out = gct.process_techtree_node_file(NODE_FIXTURE, LANG)
    # frontmatter title via the {name} template
    assert f'title: "{t(LANG, "techtree", "node_title").replace("{name}", "Braviar ECCM")}"' in out
    # frontmatter description via the {name}/{category} template
    expected_desc = t(LANG, "techtree", "node_desc_fm").replace(
        "{name}", "Braviar ECCM").replace("{category}", "Common (second set)")
    assert f'description: "{expected_desc}"' in out
    # H1, intro, table fields, end-of-line
    assert f"# {t(LANG, 'techtree', 'node_h1').replace('{name}', 'Braviar ECCM')}" in out
    assert t(LANG, "techtree", "node_end_of_line") in out
    assert "– (end of line)" not in out
    # link rewriting: groups/nodes localized, items global
    assert f"(/content/techtree/groups/common2/)" not in out
    assert f"(/{LANG}/content/techtree/groups/common2/)" in out
    assert "(/content/items/named3-eccm/)" in out


def test_techtree_node_backslash_regression():
    # The node name contains m\\2315 (a backslash). re.sub replacement
    # templates would eat the backslash (\\2 → group 2); the lambda fix
    # must keep it byte-identical in title AND description.
    out = gct.process_techtree_node_file(NODE_BACKSLASH_FIXTURE, LANG)
    name = "MSD m\\2315 'Filch' sensor suppressor"
    assert f'title: "{t(LANG, "techtree", "node_title").replace("{name}", name)}"' in out
    assert out.count("m\\2315") >= 3  # title, description, H1


# -------------------------------------------------------------- plants

def test_plants_diagram_labels_translated_structure_kept():
    out = gct.process_plants_overview(PLANTS_DIAGRAM_FIXTURE, LANG)
    for key in ("diagram_sprout", "diagram_grow", "diagram_fruiting",
                "diagram_harvestable", "diagram_killed", "diagram_respawn"):
        assert f'["{t(LANG, "plants", key)}"]' in out, key
    # no English labels survive
    assert '["Sprout (stage 1)"]' not in out
    # the flow structure (node ids + edges) is untouched; labels sit on
    # first occurrence (S["…"] --> G["…"]), so check ids/edges, not lines
    assert out.count('-->') == 6
    for node in ('S["', 'G["', 'F["', 'H["', 'K["', 'R["'):
        assert node in out
    assert 'R --> S' in out  # bare re-edge (no label on S here)
    # the respawn label keeps its literal two-character backslash-n
    # (mermaid line break); it must survive the round trip
    assert "\\n" in out


def test_plants_heading_and_table():
    # the 12-column harvestable header (exactly as in the real plants.md) —
    # the generator replaces the full header line, column by column
    header = ("| Plant | Grow rate | Fertility | Spreading | Kill distance | Max slope | "
              "Altitude band | Water band | Fruit (yield) | Max amount | "
              "Health (stages) | Player seeded |")
    fixture = PLANTS_DIAGRAM_FIXTURE + (
        "\n## Harvestable plants\n\n"
        "Species with a fruiting stage — the fruit is the harvestable yield (× = fruitAmount per fruiting stage).\n\n"
        + header + "\n| X | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |\n"
    )
    out = gct.process_plants_overview(fixture, LANG)
    P = lambda key: t(LANG, 'plants', key)
    assert f"## {P('harvestable')}" in out
    assert P('harvestable_intro') in out
    assert (f"| {P('col_plant')} | {P('col_grow_rate')} | {P('col_fertility')} | {P('col_spreading')} | "
            f"{P('col_kill_distance')} | {P('col_max_slope')} | {P('col_altitude_band')} | {P('col_water_band')} | "
            f"{P('col_fruit_yield')} | {P('col_max_amount')} | {P('col_health_stages')} | {P('col_player_seeded')} |") in out
    assert header not in out
