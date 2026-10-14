"""tools/regen_search_index.py — search index from markdown front-matter.

The script is import-unsafe (it scans on import), so it is driven via
subprocess against a fixture tree.
"""
import json
from pathlib import Path

from conftest import run_tool


def _tree(tmp_path: Path):
    c = tmp_path / "content"
    (c / "features").mkdir(parents=True)
    (c / "zones").mkdir()
    (c / "static_parent").mkdir()
    (tmp_path / "static").mkdir()

    (c / "_index.md").write_text(
        '---\ntitle: "Home"\ndescription: "The home page"\n---\n\nbody\n')
    (c / "features" / "_index.md").write_text(
        '---\ntitle: "Features"\n---\n\nbody\n')
    (c / "features" / "research.md").write_text(
        '---\ntitle: "Research"\ndescription: "How research works"\n---\n\nbody\n')
    (c / "zones" / "zone_tm.md").write_text(
        '---\ntitle: "TM"\ndescription: "The Matriarkh & more <PvP> \'fun\' + pain"\n---\n')
    # no title → skipped entirely
    (c / "zones" / "orphan.md").write_text("just a body, no front-matter\n")
    # unterminated front-matter → skipped
    (c / "zones" / "broken.md").write_text("---\ntitle: \"No end\n")
    return c


def test_index_entries_and_urls(tmp_path):
    _tree(tmp_path)
    r = run_tool("regen_search_index.py", tmp_path)
    assert r.returncode == 0, r.stderr
    out = json.loads((tmp_path / "static" / "search_index.json").read_text())
    assert out == [
        {"t": "Home", "d": "The home page", "u": "/"},
        {"t": "Features", "d": "", "u": "/features/"},
        {"t": "Research", "d": "How research works", "u": "/features/research/"},
        {"t": "TM", "d": "The Matriarkh & more <PvP> 'fun' + pain", "u": "/zones/zone-tm/"},
    ]


def test_dotnet_default_encoder_escaping(tmp_path):
    _tree(tmp_path)
    run_tool("regen_search_index.py", tmp_path)
    raw = (tmp_path / "static" / "search_index.json").read_text()
    # .NET JavaScriptEncoder.Default escapes these; json.dumps would not
    for esc in ("\\u0026", "\\u003c", "\\u003e", "\\u0027", "\\u002b"):
        assert esc in raw, f"missing .NET escape {esc}"
    assert "&" not in raw
    assert "<" not in raw


def test_underscores_become_hyphens_in_urls(tmp_path):
    c = tmp_path / "content"
    c.mkdir()
    (tmp_path / "static").mkdir()
    (c / "zone_a_b.md").write_text('---\ntitle: "Z"\n---\n')
    r = run_tool("regen_search_index.py", tmp_path)
    assert r.returncode == 0, r.stderr
    out = json.loads((tmp_path / "static" / "search_index.json").read_text())
    assert out[0]["u"] == "/zone-a-b/"
