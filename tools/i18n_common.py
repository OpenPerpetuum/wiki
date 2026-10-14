"""Shared helpers for the localized-page generators (gen_content_translations.py,
gen_zone_translations.py).

All translatable strings live in translations/<lang>.json (single source of
truth). The generators look them up by key path with automatic fallback to
the English baseline (translations/en.json):

    from i18n_common import t
    heading = t("fr", "labels", "class")          # labels.class for fr
    body    = t("cs", "zones", "pages", "protection", "body")

Sections in each translations/<lang>.json:
    ui        — UI chrome (topbar, nav, search, footer) — used by gen_i18n.py
    names     — game name translations (data-def) — used by gen_i18n.py
    labels    — common table/field labels
    robots    — robot class names, section titles, descriptions
    ores      — ore extraction tables & spawning headers
    missions  — mission/reward card labels
    extensions— extension card labels
    shop      — shop table headers
    techtree  — tech tree node labels
    zones     — zone pages: protection/levels prose, zone facts, intro templates

Adding a language = add translations/<new_lang>.json (any missing key falls
back to English) and add the code to the generators' LANGUAGES list.
"""
import json
import re
from pathlib import Path

# Repo root = parent of tools/
BASE = Path(__file__).resolve().parent.parent

# Content sections that get a /{lang}/ route prefix (see config.toml).
TRANSLATED_CONTENT_SECTIONS = [
    "ores", "plants", "missions", "deployables", "robots",
    "recipes", "techtree", "extensions", "stat-reference", "shop"
]


def load_translations(base=None):
    """Load every translations/<lang>.json → {lang_code: parsed_dict}."""
    base = Path(base) if base is not None else BASE / "translations"
    translations = {}
    for path in sorted(base.glob("*.json")):
        with open(path, "r", encoding="utf-8") as fh:
            translations[path.stem] = json.load(fh)
    return translations


TRANSLATIONS = load_translations()


def t(lang, *path):
    """Look up a string by language + nested key path, e.g.
    t("fr", "labels", "class") or t("cs", "zones", "pages", "protection", "body").

    Falls back to the English baseline, then to the last path element (the
    key itself), so a missing key degrades gracefully instead of crashing.
    """
    for l in (lang, "en"):
        node = TRANSLATIONS.get(l)
        for part in path:
            if not isinstance(node, dict):
                node = None
                break
            node = node.get(part)
        if isinstance(node, str) and node != "":
            return node
    return path[-1]


def rewrite_links(text, lang):
    """Rewrite absolute links to include the language prefix for translated sections."""
    # Pattern for markdown links: [text](/path/)
    # and HTML links: href="/path/"

    def repl_href(m):
        prefix = m.group(1)  # 'href="' or ']('
        path = m.group(2)
        suffix = m.group(3)  # '"' or ')'

        # Exclude anchor-only or full URLs
        if path.startswith("http://") or path.startswith("https://") or path.startswith("#"):
            return m.group(0)

        # Localized zones routes
        if path in ("/zones/", "/zones/protection/", "/zones/protection"):
            return f"{prefix}/{lang}{path}{suffix}"

        # Exclude unlocalized global paths
        if path.startswith("/content/items/") or path.startswith("/zones/"):
            return m.group(0)

        # Features, formats, menu routes
        for sec in ("features", "formats", "menu"):
            if path == f"/{sec}/" or path.startswith(f"/{sec}/"):
                return f"{prefix}/{lang}{path}{suffix}"

        # Root content index
        if path == "/content/":
            return f"{prefix}/{lang}/content/{suffix}"

        # Subsections in content
        for sec in TRANSLATED_CONTENT_SECTIONS:
            if path == f"/content/{sec}/" or path.startswith(f"/content/{sec}/"):
                return f"{prefix}/{lang}{path}{suffix}"

        # Root or other pages
        if path == "/":
            return f"{prefix}/{lang}/{suffix}"

        return m.group(0)

    # Replace href="..."
    text = re.sub(r'(href=["\'])(/[^"\']*)(["\'])', repl_href, text)
    # Replace markdown links: ](/path/)
    text = re.sub(r'(\]\()(/[^)\s]+)(\))', repl_href, text)
    return text
