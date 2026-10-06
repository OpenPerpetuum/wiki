# Translations

The wiki supports multiple languages for its UI chrome (nav, topbar, search,
footer) and game names (items, ores, zones). Content prose stays in the
default language (English) until per-language content is available.

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
    "...": "all 105 UI keys (see translations/en.json for the full list)"
  },
  "names": {
    "crude": "Rohöl",
    "titan": "Titan",
    "zone_tm": "Neu-Virginia",
    "zone_asi": "Daoden",
    "...": "game item/ore/zone names"
  }
}
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `lang` | yes | Language code (BCP 47): `"en"`, `"fr"`, `"de"`, ... |
| `name` | yes | Display name for the language menu: `"Français"`, `"Deutsch"` |
| `ui` | yes | UI chrome strings. Keys must match `translations/en.json`. |
| `names` | no | Game name translations. Empty `{}` = no name translation (English names shown). |

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

See `translations/en.json` for the full list (105 keys). The main groups:

- `nav_*` — sidenav labels (groups, items, sub-items)
- `search_*` — search box placeholder, results count
- `aria_*` — accessibility labels
- `palette_*`, `cb_*` — accent color + colorblind mode menus
- `zonemap_*` — zone map display mode buttons
- `foot_*` — footer links + credit text

## How it works (technical)

### Build time

```
translations/*.json
       │
       ▼
tools/gen_i18n.py ──→ static/i18n.js  (all languages' UI + names in one file)
       │
       ▼
Zola build ──→ public/  (site HTML with data-i18n/data-def attributes)
       │
       ▼
tools/tag_defs.py ──→ public/  (adds data-def="slug" to item/ore/zone links)
```

### Runtime

`static/i18n.js` (loaded in `<head>`):
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

### What does NOT get translated (yet)

- Page body prose (paragraphs, descriptions) — Phase 2
- Mermaid diagram labels — would need generator changes
- Zone map SVG labels — generated, language-neutral

## Regenerating after changes

```bash
# After editing a translations/*.json file:
make build

# To regenerate just the i18n.js (without a full Zola build):
make i18n

# To re-run the data-def tagging (after a Zola build):
python3 tools/tag_defs.py public
```

## Extracting game names for a new language

The game client ships per-language string files. To create the `names` dict:

1. Extract the client's string file for the target language (GBF format)
2. Map each `def_*` name to its display name
3. Strip the `def_` prefix for items/ores; keep `zone_*` for zones
4. Add to your `translations/<lang>.json` under `"names"`

A helper script for this will be added when the first non-English client
string file is available.
