# Translations

The wiki supports multiple languages for its UI chrome (nav, topbar, search,
footer), game names (items, ores, zones), and generated content pages (robots,
ores, missions, extensions, shop, techtree, zones). All translatable strings
live in `translations/<lang>.json` — the single source of truth consumed both
by the i18n runtime (`static/i18n.js`) and by the content generators.

Content pages are generated per language into `content/<lang>/...` at build
time (see `make i18n`). Hand-written prose pages (e.g. `zone_tm.md` worked
examples) are managed by translators per language and are never regenerated.

## Adding a new language

**Drop a JSON file in `translations/` and rebuild.**

```bash
# 1. Create the file (e.g. translations/de.json)
# 2. Rebuild:
make build
```

That's it. The build pipeline:
1. `tools/gen_i18n.py` reads all `translations/*.json` → generates `static/i18n.js`
2. Zola builds the site (picks up the new `i18n.js`)
3. `tools/tag_defs.py` adds `data-def` attributes to name links in the built HTML
4. The language menu in the topbar automatically shows all available languages

## File format

```json
{
  "lang": "de",
  "name": "Deutsch",
  "ui": {
    "nav_home": "Startseite",
    "nav_start": "Starten",
    "search_placeholder": "Wiki durchsuchen…  (Strg+F)",
    "...": "all 142 UI keys (see translations/en.json for the full list)"
  },
  "names": {
    "crude": "Rohöl",
    "titan": "Titan",
    "zone_tm": "Neu-Virginia",
    "zone_asi": "Daoden",
    "...": "game item/ore/zone names"
  },
  "labels": { "...": "shared table/field labels (27 keys)" },
  "robots": { "...": "robot table labels + per-robot text (42 keys)" },
  "ores": { "...": "ore labels, intro/spawn templates, overview prose (27 keys)" },
  "missions": { "...": "mission labels + intro (7 keys)" },
  "extensions": { "...": "extension labels + intro prose (7 keys)" },
  "shop": { "...": "shop labels, vendor locations, legends, intros (20 keys)" },
  "techtree": { "...": "techtree labels, category/node templates, index prose (27 keys)" },
  "zones": { "...": "zone page labels, intro templates, family/overview prose,
                  world-map legend + tooltips (90 keys)" },
  "deployables": { "...": "category names, descriptions, overview prose (24 keys)" },
  "plants": { "...": "field/zone legends, overview prose, growth diagram labels (35 keys)" },
  "stat_reference": { "...": "intro + per-stat legend (5 keys)" },
  "recipes": { "...": "intro (1 key)" },
  "content_index": { "...": "content index lines (2 keys)" }
}
```

The content sections (`labels` … `zones`) are looked up by key path by the
generators via `tools/i18n_common.py` (`t(lang, "zones", "fact")`). Any key
missing from a language file falls back to `translations/en.json`.

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `lang` | yes | Language code (BCP 47): `"en"`, `"fr"`, `"de"`, ... |
| `name` | yes | Display name for the language menu: `"Français"`, `"Deutsch"` |
| `ui` | yes | UI chrome strings. Keys must match `translations/en.json`. |
| `names` | no | Game name translations. Empty `{}` = no name translation (English names shown). |
| `labels`…`zones` | no | Content-page strings for the generators. Missing keys fall back to English. |

### `names` keys

The key is the **URL slug** — the last path segment of the page URL, exactly as it appears:

| Page type | URL pattern | Key | Example |
|-----------|-------------|-----|---------|
| Item | `/content/items/alligior/` | `"alligior"` | `"alligior": "Alligior"` |
| Ore | `/content/ores/crude/` | `"crude"` | `"crude": "Brut"` |
| Zone | `/zones/zone-tm/` | `"zone-tm"` | `"zone-tm": "Virginie Nouvelle"` |
| Zone (multi-word) | `/zones/zone-asi-a-real/` | `"zone-asi-a-real"` | `"zone-asi-a-real": "Hokkogaros"` |

The key is always the URL slug (all lowercase, hyphens). No `def_` prefix, no underscores.

If a name is missing from the `names` dict, the English name is shown
(fallback). You don't need to translate every single name — partial
translations are fine.

### `ui` keys

See `translations/en.json` for the full list (142 keys). The main groups:

- `nav_*` — sidenav labels (groups, items, sub-items); these double as the
  searchable labels of `static/menu_tree.json`
- `search_*` — search box placeholder (ends with the shortcut hint
  `(/ or Ctrl+F or Cmd+F)` — keep the hint verbatim; the handlers live in
  `templates/base.html`), results count
- `aria_*` — accessibility labels
- `palette_*`, `cb_*` — accent color + colorblind mode menus
- `zonemap_*` — zone-map display-mode buttons + the landmarks panel that
  `static/zone-map.js` builds at runtime on zone pages (toggle, toggle-all,
  the five landmark rows, reset-zoom title); wired into `window.WIKI_UI` by
  `applyLang()` in the generated `static/i18n.js`
- `foot_*` — footer links + credit text

## How it works (technical)

### Build time

```
translations/*.json
       │
       ├──→ tools/gen_content_translations.py ──→ content/<lang>/...  (robots, ores,
       │                                          missions, extensions, shop, techtree)
       ├──→ tools/gen_zone_translations.py ──────→ content/<lang>/zones/...
       │                                          (zone index, protection pages,
       │                                          79 generated zone pages)
       ├──→ tools/gen_i18n.py ───────────────────→ static/i18n.js
       │                                          (all languages' UI + names in one file)
       └──→ tools/gen_menu_tree.py ──────────────→ static/menu_tree.json
                                                    (sidenav links from templates/base.html:
                                                     label key/literal + href + breadcrumb;
                                                     merged into the search index at runtime)
       ▼
Zola build ──→ public/  (site HTML with data-i18n/data-def attributes)
       │
       ▼
tools/tag_defs.py ──→ public/  (adds data-def="slug" to item/ore/zone links)
```

The generators read the English source pages from `content/`, apply the
per-language lookups, and write `content/<lang>/...`. English itself is never
generated — `content/` is the English source of truth.

### Search

`static/search.js` searches `static/search_index.json` (page title + description
+ URL, one entry per page in every language). On top of that it merges
`static/menu_tree.json` (generated from the sidenav, `tools/gen_menu_tree.py`):

- a fragmentless menu link that matches a page URL adds its label and
  breadcrumb to that page's search space, so sidenav names that differ from
  the page title (e.g. "Robot stat tables" → /content/robots/) are found too;
- sidenav anchor links (e.g. `/zones/gamma/#t0`, deployable category sections)
  become their own result rows and keep the fragment, so clicking a result
  lands on the right page/section.

Menu labels are `nav_*` UI keys resolved through `window.WIKI_I18N` for the
current language at query time — the same JSON file serves all 14 languages.
Result list keyboard navigation: ↑/↓ (Home/End) move the selection,
Enter follows it, mouse hover and the keyboard share the same selection
(see `tests/search.spec.js`).
1. Reads `localStorage('wiki-lang')` (default: `"en"`)
2. On DOM ready, calls `applyLang(lang)` which:
   - Swaps `textContent` on `[data-i18n]` elements (nav, buttons, labels)
   - Swaps `innerHTML` on `[data-i18n-html]` elements (footer credit)
   - Swaps `placeholder` on `[data-i18n-ph]` elements (search box)
   - Swaps `aria-label`/`title` on `[data-i18n-aria]` elements
   - Swaps `textContent` on `[data-def]` elements (game names in links)
   - Updates `document.title` if the page has `data-page-def`
   - Updates `window.WIKI_UI` (consumed by search.js, zone-map.js)
3. The language toggle button calls `WIKI_setLang('fr')` → saves + re-applies

### What gets translated

| Element | Mechanism | Example |
|---------|-----------|---------|
| Nav labels | `data-i18n="nav_home"` | "Home" → "Accueil" |
| Search placeholder | `data-i18n-ph="search_placeholder"` | "Search…" → "Rechercher…" |
| Item/ore names in links | `data-def="crude"` | "Crude" → "Brut" |
| Zone names in links | `data-def="zone_tm"` | "New Virginia" → "Virginie Nouvelle" |
| Page title + H1 | `data-page-def` on `<body>` | "Crude" → "Brut" |
| Footer credit | `data-i18n-html="foot_credit"` | full HTML string |

### What does NOT get translated automatically

- Hand-written prose pages (`zones/generation.md`, `zones/zone_tm.md`,
  `zones/zone_asi.md`, `zones/zone_gamma_z106.md` in each language) — managed
  by translators, the generators skip them
- Zone map SVG labels — generated, language-neutral
- The plants growth-cycle mermaid diagram **is** translated (its six node
  labels live in `plants.diagram_*`; the flow structure and the literal
  two-character `\n` line breaks stay as-is)

## Adding a content string

1. Add the key to the right section of `translations/en.json` (English value).
2. Add the translated value to each `translations/<lang>.json` (or leave it
   out to fall back to English).
3. Re-run the generators: `make i18n` (or a full `make build`).

In-game proper nouns (currency names like `shop.tm_coin`, the `zones.type_pvp`/
`zones.type_pve` abbreviations, item/ore/robot names, stat identifiers) are
present in every language file with identical English values on purpose —
they are not translated. Every other key is fully translated in all 13
languages; `tools/i18n_check.py` (run as `make i18n-check`, and as a `build`
prerequisite) fails on any missing key, empty value, or placeholder mismatch.

For new zone intro templates, the English source paragraph is matched by
regex in `tools/gen_zone_translations.py` (`translate_intro`) — add both the
template key (`zones.intro.*`) and the regex.

## Regenerating after changes

```bash
# After editing a translations/*.json file:
make build

# To regenerate just the i18n.js (without a full Zola build):
make i18n

# To re-run the data-def tagging (after a Zola build):
python3 tools/tag_defs.py public

# To validate the translation files (key parity, placeholders, empty values):
make i18n-check
```

## Testing

Two independent suites:

```bash
make test     # Playwright (tests/): runs against the BUILT site (public/).
              # One-time setup: npm install && npx playwright install chromium
make test-py  # Python (tests_py/): unit + fixture + in-place idempotency
              # tests for the generator tools, with coverage (pytest +
              # coverage, both preinstalled on this machine)
```

The Python suite's integration layer re-runs the generators in place and
asserts the output is byte-identical — so the working tree must be in a
generated state (a plain `make build` is enough). The browser suite includes
the search keyboard-navigation and landmarks-panel i18n specs
(`tests/search.spec.js`, `tests/zone-map.spec.js`).

## Extracting game names for a new language

The game client ships per-language string files. To create the `names` dict:

1. Extract the client's string file for the target language (GBF format)
2. Map each `def_*` name to its display name
3. Strip the `def_` prefix for items/ores; keep `zone_*` for zones
4. Add to your `translations/<lang>.json` under `"names"`

A helper script for this will be added when the first non-English client
string file is available.
