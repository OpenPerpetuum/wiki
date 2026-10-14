"""tools/tag_defs.py — data-def attributes for the i18n name lookup."""
from pathlib import Path

import tag_defs


def _write(tmp_path: Path, *parts: str, text: str) -> Path:
    p = tmp_path.joinpath(*parts)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


BODY = '<body class="x"><main></main></body>'


def test_item_ore_zone_links_get_data_def(tmp_path):
    p = _write(tmp_path, "index.html", text=(
        f'<a href="/content/items/alligior/">a</a>'
        f'<a href="/content/ores/crude/">o</a>'
        f'<a href="/zones/zone-tm/">z</a>'
        f'<a href="/zones/zone-map/">m</a>'
        f"{BODY}"
    ))
    n = tag_defs.process_file(p)
    out = p.read_text()
    assert 'href="/content/items/alligior/" data-def="alligior"' in out
    assert 'href="/content/ores/crude/" data-def="crude"' in out
    assert 'href="/zones/zone-tm/" data-def="zone-tm"' in out
    # zone-map is a listing page, not a data page → no data-def
    assert 'href="/zones/zone-map/">m' in out
    # the page itself is a zone data page → data-page-def on <body>
    assert n >= 3


def test_idempotent(tmp_path):
    p = _write(tmp_path, "index.html",
               text='<a href="/content/items/iron-ore/">i</a>' + BODY)
    first = tag_defs.process_file(p)
    assert first == 1
    second = tag_defs.process_file(p)
    assert second == 0  # nothing double-added
    assert p.read_text().count("data-def=") == 1


def test_items_page_sets_data_page_def(tmp_path):
    p = _write(tmp_path, "content", "items", "alligior", "index.html",
               text=BODY)
    tag_defs.process_file(p)
    assert 'data-page-def="alligior"' in p.read_text()


def test_zone_page_sets_data_page_def(tmp_path):
    p = _write(tmp_path, "zones", "zone-asi-a-real", "index.html", text=BODY)
    tag_defs.process_file(p)
    assert 'data-page-def="zone-asi-a-real"' in p.read_text()


def test_zone_def_excludes_listing_pages():
    assert tag_defs.zone_def("zone-map") is None
    assert tag_defs.zone_def("zone-alpha") is None
    assert tag_defs.zone_def("zone-index") is None
    assert tag_defs.zone_def("zone-tm") == "zone-tm"
