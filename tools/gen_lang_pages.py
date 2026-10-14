#!/usr/bin/env python3
"""Generate static/lang-pages.json: a map of language → list of page paths.

The i18n runtime uses this to check if a translated version of the current
page exists before navigating. If the page isn't in the list, the switcher
only swaps the chrome (stays on the current page).

Usage:
  python3 tools/gen_lang_pages.py <content-dir> [output-file]

  content-dir   defaults to "content"
  output-file   defaults to "static/lang-pages.json"
"""
import json
import re
import sys
from pathlib import Path


def slugify(name):
    """Page-name slug as Zola renders it (slug crate): lowercase, runs of
    non-alphanumerics (including underscores) become single hyphens."""
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or name


def main():
    content_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "content")
    out_file = Path(sys.argv[2] if len(sys.argv) > 2 else "static/lang-pages.json")

    result = {}

    import re
    lang_re = re.compile(r'^[a-z]{2,3}(-[A-Z]{2})?$')

    for md_file in content_dir.rglob("*.md"):
        # Build the page path from the path RELATIVE to content_dir — never
        # from md_file.parts (that would pick up the cwd/absolute prefix when
        # content_dir is an absolute path and mislabel the language).
        #   content/fr/features/faq.md → /fr/features/faq/
        # The page-name segment is slugified the way Zola renders it, so the
        # manifest matches real URLs (e.g. deployable_fields.md →
        # /fr/formats/deployable-fields/).
        parts = list(md_file.relative_to(content_dir).parts)
        if len(parts) < 2:
            continue  # content/_index.md
        # parts[0] = language code
        # Skip the default language (English) — it's the base path
        lang = parts[0]
        if lang == "en" or not lang_re.match(lang):
            continue  # not a language dir (e.g. "features", "zones", "content")
        name, _ext = parts[-1].rsplit(".", 1)
        if name == "_index":
            # section index → the section root: /ru/features/
            parts = parts[:-1]
            page_path = "/" + "/".join(parts)
        else:
            parts[-1] = slugify(name)
            page_path = "/" + "/".join(parts)
        # _index.md → the section root
        if page_path.endswith("/_index"):
            page_path = page_path[: -len("_index")]
        if lang not in result:
            result[lang] = []
        result[lang].append(page_path)

    # Sort for deterministic output
    for lang in result:
        result[lang].sort()

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")

    total = sum(len(v) for v in result.values())
    print(f"gen_lang_pages: {total} translated pages → {out_file}")
    for lang, pages in sorted(result.items()):
        print(f"  {lang}: {len(pages)} pages")


if __name__ == "__main__":
    main()
