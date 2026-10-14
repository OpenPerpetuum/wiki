"""tools/gen_i18n.py — builds static/i18n.js from translations/*.json."""
import json

from conftest import REPO, run_tool


def test_fixture_run_produces_expected_js(tmp_path):
    d = tmp_path / "translations"
    d.mkdir()
    (d / "en.json").write_text(json.dumps({
        "lang": "en", "name": "English",
        "ui": {"hello": "Hello", "tpl": "{n} pages"},
        "names": {"titan": "Titan"},
    }))
    (d / "fr.json").write_text(json.dumps({
        "lang": "fr", "name": "Français",
        "ui": {"hello": "Bonjour"},
        "names": {"titan": "Titane"},
    }))
    r = run_tool("gen_i18n.py", d, tmp_path / "i18n.js")
    assert r.returncode == 0, r.stderr
    js = (tmp_path / "i18n.js").read_text(encoding="utf-8")

    # language list: English first, then alphabetical
    assert js.index('code:"en"') < js.index('code:"fr"')
    # per-language strings + game names
    assert "hello: \"Hello\"" in js
    assert "hello: \"Bonjour\"" in js
    assert 'WIKI_NAMES' in js and '"titan": "Titane"' in js
    # the WIKI_UI bridge for the runtime-built zone-map panel
    for camel in ("zonemapLandmarks", "zonemapLmTeleports", "zonemapResetZoom",
                  "searchNoResults", "zonemapModeHeight"):
        assert camel in js, f"WIKI_UI bridge missing {camel}"
    # runtime API
    assert "window.WIKI_applyLang" in js


def test_no_valid_files_exits_1(tmp_path):
    d = tmp_path / "translations"
    d.mkdir()
    (d / "en.json").write_text(json.dumps({"lang": "en"}))  # no ui section
    r = run_tool("gen_i18n.py", d, tmp_path / "i18n.js")
    assert r.returncode == 1


def test_real_repo_is_idempotent():
    # Regenerating against the real translations must reproduce the
    # working-tree static/i18n.js byte for byte. (cwd matters: the script
    # pre-embeds static/lang-pages.json relative to the cwd.)
    r = run_tool("gen_i18n.py", REPO / "translations", REPO / "static" / "i18n.js.tmp",
                 cwd=REPO)
    assert r.returncode == 0, r.stderr
    produced = (REPO / "static" / "i18n.js.tmp").read_text(encoding="utf-8")
    current = (REPO / "static" / "i18n.js").read_text(encoding="utf-8")
    assert produced == current
    (REPO / "static" / "i18n.js.tmp").unlink()
