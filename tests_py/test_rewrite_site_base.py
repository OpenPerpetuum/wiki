"""tools/rewrite_site_base.py — subpath deploy rewriter."""
from pathlib import Path

from conftest import run_tool


def _site(tmp_path: Path):
    site = tmp_path / "public"
    (site / "zones").mkdir(parents=True)
    (site / "index.html").write_text(
        '<a href="/zones/map/">m</a><img src="/img/x.png">'
        '<a href="//cdn.example.com/x.js"></a><a href="#a"></a>'
        '<a href="relative.html"></a>'
    )
    (site / "zones" / "map.svg").write_text('<image href="/img/t.png"/>')
    (site / "notes.txt").write_text('href="/should-not-change/"')  # not html/svg
    return site


def test_prefixes_site_absolute_links(tmp_path):
    site = _site(tmp_path)
    r = run_tool("rewrite_site_base.py", site, "https://ex.com/wiki")
    assert r.returncode == 0, r.stderr
    html = (site / "index.html").read_text()
    assert 'href="/wiki/zones/map/"' in html
    assert 'src="/wiki/img/x.png"' in html
    # protocol / hash / relative links untouched
    assert 'href="//cdn.example.com/x.js"' in html
    assert 'href="#a"' in html
    assert 'href="relative.html"' in html
    # non-HTML files untouched
    assert "/should-not-change/" in (site / "notes.txt").read_text()
    # SVG image hrefs prefixed too
    assert 'href="/wiki/img/t.png"' in (site / "zones" / "map.svg").read_text()


def test_idempotent(tmp_path):
    site = _site(tmp_path)
    run_tool("rewrite_site_base.py", site, "https://ex.com/wiki")
    before = (site / "index.html").read_text()
    r = run_tool("rewrite_site_base.py", site, "https://ex.com/wiki")
    assert r.returncode == 0, r.stderr
    assert (site / "index.html").read_text() == before


def test_base_without_path_part_is_a_noop(tmp_path):
    site = _site(tmp_path)
    r = run_tool("rewrite_site_base.py", site, "https://ex.com")
    assert r.returncode == 0, r.stderr
    assert "nothing to rewrite" in r.stdout
    assert 'href="/zones/map/"' in (site / "index.html").read_text()
