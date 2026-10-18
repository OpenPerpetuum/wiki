#!/usr/bin/env python3
"""Test that the colorblind mode CSS is complete and correct.

Verifies:
1. All four data-cb modes (deutan, protan, tritan, achro) have CSS rules
2. Each mode overrides the map color variables (--map-*)
3. Each mode applies a CSS filter to .zonemap and .map-zoom-wrap svg
4. The base.html template includes data-cb buttons for all four modes
5. The initial-load script restores data-cb from localStorage
6. The palette menu JS handles data-cb clicks and persists to localStorage

Run: python3 tools/test_colorblind.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = os.path.join(ROOT, "static", "style.css")
TEMPLATE = os.path.join(ROOT, "templates", "base.html")

PASS = 0
FAIL = 0

def ok(msg):
    global PASS
    PASS += 1
    print(f"  \u2713 {msg}")

def fail(msg):
    global FAIL
    FAIL += 1
    print(f"  \u2717 {msg}")

def section(title):
    print(f"\n{'='*60}\n{title}\n{'='*60}")

CB_MODES = ["deutan", "protan", "tritan", "achro"]
MAP_VARS = ["--map-tm", "--map-ics", "--map-asi", "--map-gamma", "--map-special"]
ACCENT_VARS = ["--neon", "--accent"]


# ---------------------------------------------------------------------------
# Test 1: CSS has rules for all four colorblind modes
# ---------------------------------------------------------------------------
section("Test 1: CSS rules exist for all colorblind modes")

with open(CSS) as f:
    css = f.read()

for mode in CB_MODES:
    pattern = f'html[data-cb="{mode}"]'
    if pattern in css:
        ok(f'html[data-cb="{mode}"] rule found')
    else:
        fail(f'html[data-cb="{mode}"] rule NOT found')


# ---------------------------------------------------------------------------
# Test 2: Each mode overrides map color variables
# ---------------------------------------------------------------------------
section("Test 2: Map color variables overridden per mode")

for mode in CB_MODES:
    # Extract the block for this mode
    pattern = f'html\\[data-cb="{mode}"\\]\\s*\\{{([^}}]+)\\}}'
    m = re.search(pattern, css)
    if not m:
        fail(f'Could not extract block for {mode}')
        continue
    block = m.group(1)
    missing = [v for v in MAP_VARS if v not in block]
    if missing:
        fail(f'{mode}: missing map vars: {missing}')
    else:
        ok(f'{mode}: all {len(MAP_VARS)} map vars overridden')


# ---------------------------------------------------------------------------
# Test 3: Each mode overrides accent/neon variables
# ---------------------------------------------------------------------------
section("Test 3: Accent variables overridden per mode")

for mode in CB_MODES:
    pattern = f'html\\[data-cb="{mode}"\\]\\s*\\{{([^}}]+)\\}}'
    m = re.search(pattern, css)
    if not m:
        fail(f'Could not extract block for {mode}')
        continue
    block = m.group(1)
    missing = [v for v in ACCENT_VARS if v not in block]
    if missing:
        fail(f'{mode}: missing accent vars: {missing}')
    else:
        ok(f'{mode}: accent vars overridden ({", ".join(ACCENT_VARS)})')


# ---------------------------------------------------------------------------
# Test 4: Each mode applies CSS filter to map elements
# ---------------------------------------------------------------------------
section("Test 4: CSS filter applied to map containers per mode")

filter_patterns = {
    "deutan": r'html\[data-cb="deutan"\]\s*\.zonemap',
    "protan": r'html\[data-cb="protan"\]\s*\.zonemap',
    "tritan": r'html\[data-cb="tritan"\]\s*\.zonemap',
    "achro":  r'html\[data-cb="achro"\]\s*\.zonemap',
}

for mode in CB_MODES:
    pat = filter_patterns[mode]
    m = re.search(pat, css)
    if m:
        # Verify the rule contains a filter property
        # Look ahead for filter: in the next ~200 chars
        after = css[m.end():m.end()+300]
        if 'filter:' in after:
            ok(f'{mode}: filter rule found for .zonemap')
        else:
            fail(f'{mode}: filter rule found but no filter: property')
    else:
        fail(f'{mode}: no .zonemap filter rule found')

# Also check .map-zoom-wrap svg selectors
for mode in CB_MODES:
    pat = f'html\\[data-cb="{mode}"\\]\\s*\\.map-zoom-wrap\\s*svg'
    m = re.search(pat, css)
    if m:
        ok(f'{mode}: filter rule found for .map-zoom-wrap svg')
    else:
        fail(f'{mode}: no .map-zoom-wrap svg filter rule found')


# ---------------------------------------------------------------------------
# Test 5: Template includes data-cb buttons for all modes
# ---------------------------------------------------------------------------
section("Test 5: Template has data-cb buttons for all modes")

with open(TEMPLATE) as f:
    tpl = f.read()

for mode in CB_MODES:
    if f'data-cb="{mode}"' in tpl:
        ok(f'data-cb="{mode}" button in template')
    else:
        fail(f'data-cb="{mode}" button NOT in template')


# ---------------------------------------------------------------------------
# Test 6: Initial-load script restores data-cb from localStorage
# ---------------------------------------------------------------------------
section("Test 6: Initial-load restores data-cb from localStorage")

if 'localStorage.getItem("wiki-cb")' in tpl or "localStorage.getItem('wiki-cb')" in tpl:
    ok("localStorage read for wiki-cb found in template")
else:
    fail("localStorage read for wiki-cb NOT found in template")

if 'setAttribute("data-cb"' in tpl or "setAttribute('data-cb'" in tpl:
    ok("setAttribute data-cb in initial-load script")
else:
    fail("setAttribute data-cb NOT found in template")


# ---------------------------------------------------------------------------
# Test 7: Palette menu JS handles data-cb clicks and persists
# ---------------------------------------------------------------------------
section("Test 7: Palette JS handles data-cb clicks and persistence")

if 'querySelectorAll("button[data-cb]"' in tpl or "querySelectorAll('button[data-cb]'" in tpl:
    ok("querySelectorAll for data-cb buttons found")
else:
    fail("querySelectorAll for data-cb buttons NOT found")

if 'localStorage.setItem("wiki-cb"' in tpl or "localStorage.setItem('wiki-cb'" in tpl:
    ok("localStorage.setItem wiki-cb found")
else:
    fail("localStorage.setItem wiki-cb NOT found")


# ---------------------------------------------------------------------------
# Test 8: Achro mode uses grayscale filter (sanity check)
# ---------------------------------------------------------------------------
section("Test 8: Achro mode uses grayscale filter")

m = re.search(r'html\[data-cb="achro"\]\s*\.zonemap[^{]*\{([^}]+)\}', css)
if m:
    block = m.group(1)
    if 'grayscale' in block:
        ok("achro uses grayscale filter")
    else:
        fail(f"achro filter does not contain 'grayscale': {block.strip()}")
else:
    fail("achro .zonemap rule not found")


# ---------------------------------------------------------------------------
# Test 9: Colorblind modes are independent of palette (no combined selectors)
# ---------------------------------------------------------------------------
section("Test 9: Colorblind modes independent of palette")

# Check that there are no combined [data-palette][data-cb] selectors
combined = re.findall(r'\[data-palette[^\]]*\]\[data-cb', css)
if combined:
    fail(f"Found {len(combined)} combined palette+cb selectors (should be independent)")
else:
    ok("No combined palette+cb selectors (modes are independent)")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
total = PASS + FAIL
print(f"\n{'='*60}")
print(f"Results: {PASS}/{total} passed, {FAIL} failed")
print(f"{'='*60}")

if FAIL > 0:
    sys.exit(1)
print("All colorblind mode tests passed.")
