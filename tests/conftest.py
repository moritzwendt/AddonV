"""pytest glue: repo root on sys.path and the `tmp` folder fixture the tests use."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def tmp(tmp_path: Path) -> Path:
    return tmp_path
