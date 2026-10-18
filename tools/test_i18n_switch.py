#!/usr/bin/env python3
"""Test that the i18n language live-switch logic works correctly.

Verifies:
1. lang-pages.json manifest is consistent with built pages in public/
2. translatedUrl() logic produces valid, existing URLs
3. swapContent() target pages contain an <article> element
4. The i18n.js file has no undeclared variable assignments (strict mode safety)

Run: python3 tools/test_i18n_switch.py
"""
import json
import os
import re
import sys
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "public")
STATIC = os.path.join(ROOT, "static")

PASS = 0
FAIL = 0

def ok(msg):
    global PASS
    PASS += 1
    print(f"  ✓ {msg}")

def fail(msg):
    global FAIL
    FAIL += 1
    print(f"  ✗ {msg}")

def section(title):
    print(f"\n{'='*60}\n{title}\n{'='*60}")


# ---------------------------------------------------------------------------
# Test 1: Manifest consistency
# ---------------------------------------------------------------------------
section("Test 1: lang-pages.json manifest consistency")

manifest_path = os.path.join(STATIC, "lang-pages.json")
if not os.path.exists(manifest_path):
    fail(f"Manifest not found: {manifest_path}")
    sys.exit(1)

with open(manifest_path) as f:
    manifest = json.load(f)

langs = list(manifest.keys())
ok(f"Manifest has {len(langs)} languages: {', '.join(langs[:5])}...")

# Check that manifest entries correspond to existing files in public/
sample_size = 20  # Check a sample for speed
import random
random.seed(42)

total_checked = 0
total_missing = 0
for lang in langs[:3]:  # Check first 3 languages
    pages = manifest[lang]
    sample = random.sample(pages, min(sample_size, len(pages)))
    for page in sample:
        # Manifest paths like /de/features/character → public/de/features/character/index.html
        # Or /de/ → public/de/index.html
        if page.endswith("/"):
            fpath = os.path.join(PUB, page.lstrip("/"), "index.html")
        else:
            fpath = os.path.join(PUB, page.lstrip("/"), "index.html")
            if not os.path.exists(fpath):
                # Try without index.html (might be a direct file)
                fpath2 = os.path.join(PUB, page.lstrip("/"))
                if os.path.exists(fpath2):
                    total_checked += 1
                    continue
        if not os.path.exists(fpath):
            total_missing += 1
            if total_missing <= 3:
                fail(f"Missing: {page} → {fpath}")
        total_checked += 1

if total_missing == 0:
    ok(f"All {total_checked} sampled pages exist in public/")
else:
    fail(f"{total_missing}/{total_checked} sampled pages missing from public/")


# ---------------------------------------------------------------------------
# Test 2: translatedUrl() logic simulation
# ---------------------------------------------------------------------------
section("Test 2: translatedUrl() logic simulation")

DEFAULT_LANG = "en"

def simulated_translated_url(current_pathname, target_lang, manifest, root_path=""):
    """Simulate the JS translatedUrl() function."""
    # sitePath: strip root path
    path = current_pathname
    if root_path and path.startswith(root_path):
        path = path[len(root_path):] or "/"
    if not path.startswith("/"):
        path = "/" + path

    # Strip current language prefix
    current_prefix = ""
    m = re.match(r'^/([a-z]{2,3}(?:-[A-Z]{2})?)(/|$)', path)
    if m and m.group(1) != DEFAULT_LANG and m.group(1) in manifest:
        current_prefix = "/" + m.group(1)

    base_path = path[len(current_prefix):] if current_prefix else path
    if base_path:
        base_path = base_path or "/"
    if not base_path.startswith("/"):
        base_path = "/" + base_path

    if target_lang == DEFAULT_LANG:
        if current_prefix and base_path != path:
            return root_path + base_path
        return None  # already on default language

    if target_lang not in manifest:
        return None

    target = "/" + target_lang + base_path
    target = re.sub(r'//+', '/', target)

    pages = manifest[target_lang]
    for p in pages:
        if p == target or p + "/" == target:
            return root_path + target
    return None


# Test cases: (current_url, target_lang, expected_result)
test_cases = [
    # English → German
    ("/features/character/", "de", "/de/features/character/"),
    ("/zones/map/", "fr", "/fr/zones/map/"),
    ("/", "de", "/de/"),
    ("/content/deployables/", "ja", "/ja/content/deployables/"),
    # German → English (back)
    ("/de/features/character/", "en", "/features/character/"),
    # German → French (language switch)
    ("/de/features/character/", "fr", "/fr/features/character/"),
    # Already on target (function returns URL but setLang skips swap since url === pathname)
    ("/de/features/character/", "de", "/de/features/character/"),
    # Home page
    ("/", "fr", "/fr/"),
    # Nested page (use a page that exists in Korean)
    ("/features/research/", "ko", "/ko/features/research/"),
]

all_pass = True
for current, target_lang, expected in test_cases:
    result = simulated_translated_url(current, target_lang, manifest)
    # Normalize: the JS function returns the URL with trailing slash from basePath
    # Our simulation should match
    if expected is None:
        if result is None:
            ok(f"{current} → {target_lang}: None (correct)")
        else:
            fail(f"{current} → {target_lang}: expected None, got {result}")
            all_pass = False
    else:
        # The JS returns rp + target where target includes trailing slash from basePath
        # Normalize for comparison
        if result is None:
            fail(f"{current} → {target_lang}: expected {expected}, got None")
            all_pass = False
        else:
            # Normalize trailing slash for comparison
            r_norm = result.rstrip("/")
            e_norm = expected.rstrip("/")
            if r_norm == e_norm:
                ok(f"{current} → {target_lang}: {result}")
            else:
                fail(f"{current} → {target_lang}: expected {expected}, got {result}")
                all_pass = False


# ---------------------------------------------------------------------------
# Test 3: Target pages contain <article>
# ---------------------------------------------------------------------------
section("Test 3: Translated pages contain <article> element")

# Check a sample of translated pages have an <article> tag
article_check_paths = [
    "de/features/character/index.html",
    "fr/zones/map/index.html",
    "de/index.html",
    "ja/content/deployables/index.html",
    "ko/features/research/index.html",
]

all_have_article = True
for rel in article_check_paths:
    fpath = os.path.join(PUB, rel)
    if not os.path.exists(fpath):
        fail(f"File not found: {rel}")
        all_have_article = False
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    if "<article" in content:
        ok(f"{rel}: has <article>")
    else:
        fail(f"{rel}: MISSING <article>")
        all_have_article = False


# ---------------------------------------------------------------------------
# Test 4: i18n.js strict mode safety (no undeclared assignments)
# ---------------------------------------------------------------------------
section("Test 4: i18n.js strict mode safety")

i18n_path = os.path.join(STATIC, "i18n.js")
with open(i18n_path, "r", encoding="utf-8") as f:
    js_content = f.read()

# Check that the file uses strict mode
if "'use strict'" in js_content or '"use strict"' in js_content:
    ok("File uses 'use strict'")
else:
    fail("File does NOT use 'use strict' (undeclared vars won't throw)")

# Extract all variable declarations
declared_vars = set(re.findall(r'\bvar\s+([A-Za-z_$][A-Za-z0-9_$]*)', js_content))
declared_vars |= set(re.findall(r'\blet\s+([A-Za-z_$][A-Za-z0-9_$]*)', js_content))
declared_vars |= set(re.findall(r'\bconst\s+([A-Za-z_$][A-Za-z0-9_$]*)', js_content))

# Also add function parameters and common globals
globals_ok = {
    'window', 'document', 'localStorage', 'navigator', 'history',
    'fetch', 'DOMParser', 'CustomEvent', 'requestAnimationFrame',
    'console', 'Math', 'JSON', 'Object', 'Array', 'String', 'Number',
    'Boolean', 'Error', 'RegExp', 'Set', 'Map', 'Promise',
    'MutationObserver', 'parseInt', 'parseFloat', 'isNaN',
    'setTimeout', 'clearTimeout', 'setInterval', 'clearInterval',
    'encodeURIComponent', 'decodeURIComponent',
}

# Find all assignments to uppercase constants (potential undeclared vars)
# Pattern: WORD = value (not var/let/const WORD, not obj.WORD, not this.WORD)
assignments = re.findall(r'^(?!.*\b(var|let|const)\s)(?!.*\.)\b([A-Z][A-Z_]{2,})\s*=', js_content, re.MULTILINE)

undeclared = []
for _, varname in assignments:
    if varname in declared_vars or varname in globals_ok:
        continue
    # Check if it's a function parameter or local
    # Simple heuristic: if it's declared with var anywhere, it's fine
    if varname in declared_vars:
        continue
    undeclared.append(varname)

if undeclared:
    # Filter out false positives (object properties, etc.)
    real_issues = []
    for v in undeclared:
        # Check if it's actually assigned at top level (not as a property)
        pattern = rf'^(?!.*\b(var|let|const)\s)(?!.*\.)\b{v}\s*='
        if re.search(pattern, js_content, re.MULTILINE):
            real_issues.append(v)
    if real_issues:
        fail(f"Potentially undeclared assignments: {real_issues}")
    else:
        ok("No undeclared variable assignments detected")
else:
    ok("No undeclared variable assignments detected")

# Specifically check LANG_PAGES is declared
if 'var LANG_PAGES' in js_content or 'let LANG_PAGES' in js_content or 'const LANG_PAGES' in js_content:
    ok("LANG_PAGES is properly declared")
else:
    # Check if it's initialized inline (var LANG_PAGES = {...})
    if re.search(r'\bvar\s+LANG_PAGES\b', js_content):
        ok("LANG_PAGES is properly declared")
    else:
        fail("LANG_PAGES is NOT declared with var/let/const (will throw in strict mode)")


# ---------------------------------------------------------------------------
# Test 5: swapContent function exists and has error handling
# ---------------------------------------------------------------------------
section("Test 5: swapContent function structure")

if 'function swapContent' in js_content:
    ok("swapContent function exists")
else:
    fail("swapContent function NOT found")

if '.catch(' in js_content:
    ok("swapContent has .catch() error handler")
else:
    fail("swapContent missing .catch() error handler")

if 'window.location.href' in js_content:
    ok("Fallback to full navigation present")
else:
    fail("No fallback navigation found")

if 'WIKI_rescanZoneMaps' in js_content:
    ok("Zone map re-scan called after swap")
else:
    fail("Zone map re-scan NOT called after swap")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
section("Summary")
total = PASS + FAIL
print(f"\n  {PASS}/{total} checks passed, {FAIL} failed")
if FAIL > 0:
    print("\n  ❌ TESTS FAILED")
    sys.exit(1)
else:
    print("\n  ✅ ALL TESTS PASSED")
    sys.exit(0)
