"""tools/i18n_common.py — t() lookup + rewrite_links()."""
import i18n_common


# ---------------------------------------------------------------- t()

def test_t_real_repo_lookup():
    # A key that exists for every language must return a non-empty string
    # and never the raw key.
    for lang in ("en", "fr", "ru", "zh-CN"):
        v = i18n_common.t(lang, "labels", "class")
        assert isinstance(v, str) and v and v != "class"


def test_t_missing_lang_falls_back_to_english():
    assert i18n_common.t("xx", "labels", "class") == i18n_common.t("en", "labels", "class")


def test_t_missing_key_falls_back_to_key_name():
    assert i18n_common.t("fr", "no_such_section", "no_such_key") == "no_such_key"


def test_t_nested_lookup_and_fallbacks(monkeypatch):
    monkeypatch.setattr(i18n_common, "TRANSLATIONS", {
        "en": {"a": {"b": "english value"}, "a": None},  # 'a' redefined below
    })
    # rebuild a clean fixture (dict literal above collapsed 'a'); use fresh:
    monkeypatch.setattr(i18n_common, "TRANSLATIONS", {
        "en": {"a": {"b": "english value"}, "only_en": "x"},
        "fr": {"a": {"b": "valeur française"}},
    })
    assert i18n_common.t("fr", "a", "b") == "valeur française"
    # missing in fr → English fallback
    assert i18n_common.t("fr", "only_en") == "x"
    # missing everywhere → the key itself
    assert i18n_common.t("fr", "nope", "missing") == "missing"


def test_t_empty_string_is_not_a_value(monkeypatch):
    monkeypatch.setattr(i18n_common, "TRANSLATIONS", {
        "en": {"k": "english"},
        "fr": {"k": ""},
    })
    # empty translation degrades to the English baseline, not the key
    assert i18n_common.t("fr", "k") == "english"


def test_t_non_dict_node_degrades(monkeypatch):
    monkeypatch.setattr(i18n_common, "TRANSLATIONS", {
        "en": {"k": "scalar"},
    })
    assert i18n_common.t("fr", "k", "deeper") == "deeper"


# -------------------------------------------------------- rewrite_links()

def test_rewrite_links_translated_sections():
    rw = i18n_common.rewrite_links
    assert rw("[Ores](/content/ores/)", "fr") == "[Ores](/fr/content/ores/)"
    assert rw('<a href="/content/robots/x/">', "fr") == '<a href="/fr/content/robots/x/">'
    assert rw("[Shop](/content/shop/)", "fr") == "[Shop](/fr/content/shop/)"


def test_rewrite_links_global_paths_untouched():
    rw = i18n_common.rewrite_links
    # /zones/ pages and the items catalog are global (no language prefix)
    assert rw("[Zone](/zones/gamma/)", "fr") == "[Zone](/zones/gamma/)"
    assert rw("[Item](/content/items/iron-ore/)", "fr") == "[Item](/content/items/iron-ore/)"
    assert rw("[Map](/zones/map/#t0)", "fr") == "[Map](/zones/map/#t0)"


def test_rewrite_links_zone_exceptions():
    # the zone index + protection pages ARE localized (explicit exceptions)
    rw = i18n_common.rewrite_links
    assert rw("[Index](/zones/)", "fr") == "[Index](/fr/zones/)"
    assert rw("[Prot](/zones/protection/)", "fr") == "[Prot](/fr/zones/protection/)"


def test_rewrite_links_chrome_routes():
    rw = i18n_common.rewrite_links
    assert rw("[Research](/features/research/)", "de") == "[Research](/de/features/research/)"
    assert rw("[Start](/menu/start/)", "de") == "[Start](/de/menu/start/)"
    assert rw("[Formats](/formats/)", "de") == "[Formats](/de/formats/)"
    assert rw("[Content](/content/)", "de") == "[Content](/de/content/)"
    # a bare "/" target has no path to match — left untouched by design
    assert rw("[Home](/)", "de") == "[Home](/)"


def test_rewrite_links_external_and_anchor_untouched():
    rw = i18n_common.rewrite_links
    assert rw("[X](https://a.b/)", "fr") == "[X](https://a.b/)"
    assert rw("[X](http://a.b/)", "fr") == "[X](http://a.b/)"
    assert rw("[X](#anchor)", "fr") == "[X](#anchor)"
    # relative links are not matched at all
    assert rw("[X](../zones/)", "fr") == "[X](../zones/)"
