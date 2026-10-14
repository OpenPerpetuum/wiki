"""tools/gen_menu_tree.py — sidenav parser + menu_tree.json generation."""
import json

import gen_menu_tree
from conftest import REPO, run_tool

FIXTURE = """
<html><body>
<nav id="sidenav">
  <ul>
    <li><a href="/" data-i18n="nav_home">Home</a></li>
    <li>
      <a href="/zones/map/" data-i18n="nav_zone_map">World</a>
      <ul>
        <li><a href="/zones/gamma/#t0">T0</a></li>
        <li>
          <a href="/content/shop/" data-i18n="nav_shop">Shop</a>
          <ul>
            <li><a href="/content/shop/ammo/">Ammo</a></li>
          </ul>
        </li>
      </ul>
    </li>
    <li>
      <a href="/features/research/"><span data-i18n="nav_research">Research</span></a>
    </li>
  </ul>
</nav>
<nav id="other">
  <ul><li><a href="/ignored/">Nope</a></li></ul>
</nav>
</body></html>
"""


def parse(html):
    p = gen_menu_tree.SidenavParser()
    p.feed(html)
    return p.entries


def test_flat_entries():
    e = parse(FIXTURE)
    assert {"l": "nav_home", "u": "/", "p": []} in e
    assert {"l": "nav_zone_map", "u": "/zones/map/", "p": []} in e


def test_ancestor_breadcrumbs_innermost_last():
    e = parse(FIXTURE)
    t0 = next(x for x in e if x["u"] == "/zones/gamma/#t0")
    assert t0 == {"l": "T0", "u": "/zones/gamma/#t0", "p": ["nav_zone_map"]}
    ammo = next(x for x in e if x["u"] == "/content/shop/ammo/")
    assert ammo["p"] == ["nav_zone_map", "nav_shop"]


def test_data_i18n_on_inner_span():
    # group-head links carry data-i18n on the <span>, not the <a>
    e = parse(FIXTURE)
    assert {"l": "nav_research", "u": "/features/research/", "p": []} in e


def test_other_navs_are_ignored():
    assert not any(x["u"] == "/ignored/" for x in parse(FIXTURE))


def test_link_without_href_or_label_is_dropped():
    html = """
    <nav id="sidenav"><ul>
      <li><a data-i18n="no_href">No href</a></li>
      <li><a href="/x/"></a></li>
    </ul></nav>
    """
    assert parse(html) == []


# ------------------------------------------------------- real repo run

def test_menu_tree_matches_checked_in_file(tmp_path):
    # Run the generator against a throwaway copy of the real template; the
    # output must match the committed static/menu_tree.json byte for byte.
    (tmp_path / "templates").mkdir()
    (tmp_path / "templates" / "base.html").write_text(
        (REPO / "templates" / "base.html").read_text(encoding="utf-8"),
        encoding="utf-8")
    (tmp_path / "static").mkdir()
    r = run_tool("gen_menu_tree.py", tmp_path)
    assert r.returncode == 0, r.stderr
    produced = (tmp_path / "static" / "menu_tree.json").read_text(encoding="utf-8")
    checked_in = (REPO / "static" / "menu_tree.json").read_text(encoding="utf-8")
    assert produced == checked_in


def test_menu_tree_entries_are_well_formed():
    data = json.loads((REPO / "static" / "menu_tree.json").read_text(encoding="utf-8"))
    assert len(data) >= 50  # the real sidenav has ~80 links
    for e in data:
        assert set(e) == {"l", "u", "p"}
        assert e["u"].startswith("/")
        assert isinstance(e["p"], list)
        # a label is either a nav_* i18n key or non-empty literal text
        assert e["l"].startswith("nav_") or e["l"].strip()
