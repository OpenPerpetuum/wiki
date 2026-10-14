"""Shared fixtures for the Python generator tests.

Run with the Makefile target:  make test-py
(or: python3 -m pytest tests_py -q)

The generators are pure-stdlib scripts; the tests are split in three layers:
  1. unit      — the pure functions (process_*, t, rewrite_links, parsers)
  2. fixtures  — whole scripts run against a tiny synthetic tree in tmp_path
  3. integration — the real generators run in-place; output must be
                   byte-identical (idempotent) to what is already in the tree
"""
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

# The tools import each other as top-level modules (tools/*.py do
# `sys.path.insert(0, tools)`), so mirror that here.
sys.path.insert(0, str(REPO / "tools"))


def run_tool(script, *args, cwd=None):
    """Run a tools/*.py script in a subprocess, return CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(REPO / "tools" / script), *[str(a) for a in args]],
        cwd=str(cwd) if cwd else None,
        capture_output=True, text=True,
    )


@pytest.fixture
def repo():
    return REPO
