"""Integration: the real generators run in-place and must be idempotent.

The working tree is the source of truth for "what the generators produce":
re-running every generator must leave every output file byte-identical.
If a replacement rule stops matching (a source page changed, a translation
key was renamed, …) the output differs and the test fails.

These tests also assert a handful of concrete translations so that a
consistently-wrong generator (working tree + generator out of sync) is
caught as well.
"""
import hashlib
from pathlib import Path

from conftest import REPO, run_tool

CONTENT_GENS = ["gen_content_translations.py", "gen_zone_translations.py"]
STATIC_GENS = {
    "gen_lang_pages.py": ["static/lang-pages.json"],
    "gen_i18n.py": ["static/i18n.js"],
    "gen_menu_tree.py": ["static/menu_tree.json"],
}


def _content_output_files():
    files = []
    for lang_dir in (REPO / "content").iterdir():
        if not lang_dir.is_dir():
            continue
        for sub in ("content", "zones"):
            d = lang_dir / sub
            if d.is_dir():
                files.extend(f for f in d.rglob("*") if f.is_file())
    return files


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _snapshot(files):
    return {str(f): _md5(f) for f in files}


def test_content_generators_are_idempotent():
    files = _content_output_files()
    before = _snapshot(files)
    for script in CONTENT_GENS:
        r = run_tool(script, cwd=REPO)
        assert r.returncode == 0, f"{script}: {r.stderr}"
    after = _snapshot(files)
    changed = [k for k in before if before[k] != after[k]]
    assert not changed, f"{len(changed)} files changed; first: {sorted(changed)[:5]}"


def test_static_generators_are_idempotent():
    for script, outs in STATIC_GENS.items():
        before = {p: _md5(REPO / p) for p in outs}
        args = [REPO / "translations", REPO / outs[0]] if script == "gen_i18n.py" else \
               [REPO / "content", REPO / outs[0]] if script == "gen_lang_pages.py" else \
               [REPO]
        r = run_tool(script, *args, cwd=REPO)
        assert r.returncode == 0, f"{script}: {r.stderr}"
        after = {p: _md5(REPO / p) for p in outs}
        assert before == after, f"{script} changed {outs}"


def test_spot_checks_of_generated_translations():
    # ru zone page: facts table translated
    p = (REPO / "content" / "ru" / "zones" / "zone_asi_pve.md").read_text(encoding="utf-8")
    assert "| Факт | Значение |" in p
    # fr world map: landmarks legend translated (the group the user reported)
    p = (REPO / "content" / "fr" / "zones" / "map.md").read_text(encoding="utf-8")
    assert ">Landmarks</button>" not in p
    assert "Repères" in p
    # fr plants: mermaid diagram labels translated, \n literal preserved
    p = (REPO / "content" / "fr" / "content" / "plants.md").read_text(encoding="utf-8")
    assert "La zone réapparaît vers l'objectif" in p
    assert "\\nfertility" in p
    # ru techtree node: backslash in the name survived
    p = (REPO / "content" / "ru" / "content" / "techtree" / "nodes" / "named2_sensor_dampener.md")
    assert p.exists(), "regression fixture node missing"
    p = p.read_text(encoding="utf-8")
    assert "m\\2315" in p
    # i18n.js: the zone-map landmarks panel bridge for every language
    js = (REPO / "static" / "i18n.js").read_text(encoding="utf-8")
    assert js.count("zonemapLandmarks") >= 1
    for lang in ("ru", "fr", "ja"):
        assert lang in js
