"""tools/i18n_check.py — the CI gate for translations/*.json."""
import json
import sys

import i18n_check
from conftest import run_tool


# ------------------------------------------------------- pure helpers

def test_flatten_nested_and_top_level_scalars():
    out = i18n_check.flatten({
        "lang": "fr",            # top-level scalar → skipped
        "ui": {"a": "1"},
        "zones": {"pages": {"body": "2"}},
    })
    assert out == {"ui.a": "1", "zones.pages.body": "2"}


def test_placeholders():
    assert i18n_check.placeholders("x {n} y {lang} z") == {"n", "lang"}
    assert i18n_check.placeholders("no placeholders") == set()
    assert i18n_check.placeholders(None) == set()
    # not a valid placeholder: uppercase / starting with a digit
    assert i18n_check.placeholders("{N} {1x}") == set()


# ------------------------------------------------- the real repo passes

def test_gate_passes_on_real_repo():
    r = run_tool("i18n_check.py")
    assert r.returncode == 0, r.stderr
    assert "OK — no errors" in r.stdout


# -------------------------------------------------- failure fixtures

def _write(tmp_path, en, others):
    d = tmp_path / "translations"
    d.mkdir()
    (d / "en.json").write_text(json.dumps(en), encoding="utf-8")
    for lang, data in others.items():
        (d / f"{lang}.json").write_text(json.dumps(data), encoding="utf-8")
    return d


def _run(trans_dir, monkeypatch):
    import i18n_check as ic
    monkeypatch.setattr(ic, "TRANS", trans_dir)
    monkeypatch.setattr(sys, "argv", ["i18n_check.py"])  # strip pytest args
    return ic.main()


def test_missing_key_is_an_error(tmp_path, monkeypatch):
    d = _write(tmp_path, {"ui": {"a": "x"}}, {"fr": {}})
    assert _run(d, monkeypatch) == 1


def test_placeholder_mismatch_is_an_error(tmp_path, monkeypatch):
    d = _write(tmp_path,
               {"ui": {"tpl": "hello {name}"}},
               {"fr": {"ui": {"tpl": "bonjour"}}})
    assert _run(d, monkeypatch) == 1


def test_lang_placeholder_is_allowed_in_translations(tmp_path, monkeypatch):
    # {lang} is a URL-prefix placeholder the generators fill in; it may
    # appear in translated values but never in en values.
    d = _write(tmp_path,
               {"ui": {"u": "/content/ores/"}},
               {"fr": {"ui": {"u": "/{lang}/content/ores/"}}})
    assert _run(d, monkeypatch) == 0


def test_empty_value_is_an_error(tmp_path, monkeypatch):
    d = _write(tmp_path,
               {"ui": {"a": "x"}},
               {"fr": {"ui": {"a": "   "}}})
    assert _run(d, monkeypatch) == 1


def test_extra_keys_are_warnings_not_errors(tmp_path, monkeypatch):
    d = _write(tmp_path,
               {"ui": {"a": "x"}},
               {"fr": {"ui": {"a": "y", "extra": "z"}}})
    assert _run(d, monkeypatch) == 0


def test_non_string_value_is_an_error(tmp_path, monkeypatch):
    d = _write(tmp_path,
               {"ui": {"a": "x"}},
               {"fr": {"ui": {"a": 42}}})
    assert _run(d, monkeypatch) == 1
