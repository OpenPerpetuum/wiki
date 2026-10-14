#!/usr/bin/env python3
"""i18n translation-file integrity checker (CI gate).

Validates translations/*.json:

  1. key parity   — every key present in en.json must exist in every other
                    language file. Missing keys are errors. Keys that exist in
                    a language but not in en are reported as warnings (a
                    pre-existing, documented set exists for ui/names).
  2. placeholders — the {placeholder} set of each value must match the en value
                    for the same key (a mismatch renders a literal "{link}" or
                    drops a link in the generated pages). Exception: {lang} is a
                    URL-prefix placeholder filled by the generators; it is
                    allowed in translated values (en values use root URLs and
                    never carry it).
  3. empty values — no value may be empty or whitespace-only.

Exit code 0 when there are no errors (warnings do not fail the gate).

Pure standard library. Usage:
    python3 tools/i18n_check.py          # gate mode (errors -> exit 1)
    python3 tools/i18n_check.py -v       # also print warnings
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANS = ROOT / "translations"
PLACEHOLDER_RE = re.compile(r"\{([a-z_][a-z0-9_]*)\}")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def flatten(d: dict, prefix: str = "") -> dict:
    """Flatten nested dicts to {'section.key': scalar} (skips non-dict scalars
    only at top level, e.g. 'lang'/'name')."""
    out = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(flatten(v, key))
        elif prefix:  # skip top-level scalars like 'lang', 'name'
            out[key] = v
    return out


def placeholders(value: str) -> set:
    return set(PLACEHOLDER_RE.findall(value)) if isinstance(value, str) else set()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-v", "--verbose", action="store_true", help="print warnings")
    args = ap.parse_args()

    files = {p.stem: p for p in sorted(TRANS.glob("*.json"))}
    if "en" not in files:
        print("error: translations/en.json not found", file=sys.stderr)
        return 1
    langs = [l for l in files if l != "en"]

    en = flatten(load(files["en"]))
    errors: list[str] = []
    warnings: list[str] = []

    for lang in langs:
        data = flatten(load(files[lang]))

        # 1. key parity
        for key in sorted(en):
            if key not in data:
                errors.append(f"{lang}: missing key '{key}'")
        for key in sorted(set(data) - set(en)):
            warnings.append(f"{lang}: extra key '{key}' (not in en)")

        # 2. placeholders + 3. empty values
        for key, en_val in en.items():
            val = data.get(key)
            if val is None:
                continue
            if not isinstance(val, str) or not val.strip():
                errors.append(f"{lang}: empty value for '{key}'")
                continue
            en_ph, lang_ph = placeholders(en_val), placeholders(val)
            missing = en_ph - lang_ph
            extra = lang_ph - en_ph - {"lang"}  # {lang} is a URL-prefix placeholder
            if missing or extra:
                parts = []
                if missing:
                    parts.append(f"missing {sorted(missing)}")
                if extra:
                    parts.append(f"unexpected {sorted(extra)}")
                errors.append(f"{lang}: placeholder mismatch in '{key}': {', '.join(parts)}")

    # report
    print(f"i18n check: {len(langs)} languages, {len(en)} reference keys (en)")
    for lang in langs:
        n = len(flatten(load(files[lang])))
        print(f"  {lang:<6} {n} keys")
    if args.verbose:
        for w in warnings:
            print(f"  warn: {w}")
    if errors:
        print(f"\n{len(errors)} error(s):", file=sys.stderr)
        for e in errors:
            print(f"  error: {e}", file=sys.stderr)
        return 1
    print("OK — no errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
