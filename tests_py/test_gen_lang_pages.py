"""tools/gen_lang_pages.py — the language page manifest."""
import json

import gen_lang_pages
from conftest import run_tool


def test_slugify():
    s = gen_lang_pages.slugify
    assert s("Deployable Fields") == "deployable-fields"
    assert s("x__y") == "x-y"
    assert s("Zone Index") == "zone-index"
    assert s("deployable_fields") == "deployable-fields"  # underscores too
    assert s("") == ""
    # note: accented letters are treated as non-alphanumeric here (d-j);
    # Zola's unicode-aware slug crate would keep them, but page names in
    # this repo are ASCII, so the divergence is harmless


def test_manifest_fixture(tmp_path):
    c = tmp_path / "content"
    (c / "fr" / "features").mkdir(parents=True)
    (c / "ru" / "zones").mkdir(parents=True)
    (c / "content" / "ores").mkdir(parents=True)   # not a language dir
    (c / "en" / "features").mkdir(parents=True)    # default language: skipped
    (c / "fr" / "features" / "faq.md").write_text("x")
    (c / "fr" / "features" / "_index.md").write_text("x")
    (c / "ru" / "zones" / "zone_tm.md").write_text("x")
    (c / "content" / "ores" / "iron.md").write_text("x")
    (c / "en" / "features" / "x.md").write_text("x")

    out = tmp_path / "out" / "lang-pages.json"
    r = run_tool("gen_lang_pages.py", c, out)
    assert r.returncode == 0, r.stderr
    data = json.loads(out.read_text())
    # canonical format: no trailing slashes (the runtime also accepts
    # "+ '/' matches), sorted per language
    assert data == {
        "fr": ["/fr/features", "/fr/features/faq"],
        "ru": ["/ru/zones/zone-tm"],
    }


def test_real_manifest_covers_every_localized_page(repo):
    # The manifest in the working tree must match a fresh scan of content/.
    manifest = json.loads((repo / "static" / "lang-pages.json").read_text())
    import re
    lang_re = re.compile(r"^[a-z]{2,3}(-[A-Z]{2})?$")
    fresh = {}
    for md in (repo / "content").rglob("*.md"):
        parts = list(md.relative_to(repo / "content").parts)
        if len(parts) < 2:
            continue
        lang = parts[0]
        if lang == "en" or not lang_re.match(lang):
            continue
        name = parts[-1][:-3]  # strip .md
        if name == "_index":
            path = "/" + "/".join(parts[:-1])
        else:
            path = "/" + "/".join(parts[:-1] + [gen_lang_pages.slugify(name)])
        fresh.setdefault(lang, []).append(path)
    for lang in fresh:
        fresh[lang].sort()
    assert manifest == fresh
