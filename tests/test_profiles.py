"""Unit tests for profiles.py (hiding/restoring a profile's ELS files).

Run with:  py -3 tests\\test_profiles.py   — or —  py -3 -m pytest tests
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import profiles
from _runner import run


def _els_root(tmp: Path, *files: str) -> Path:
    root = tmp / "ELS"
    live = root / profiles.PACK_DEFAULT
    live.mkdir(parents=True)
    for name in files:
        (live / name).write_text("<vcf/>")
    return root


def test_safe_folder_name():
    assert profiles.safe_folder_name("Cops & Robbers!") == "Cops  Robbers"
    assert profiles.safe_folder_name("   ") == "profile"
    assert profiles.safe_folder_name("a/b\\c") == "abc"


def test_stash_moves_files_out_of_the_live_folder(tmp: Path):
    els = _els_root(tmp, "a.xml", "b.xml")
    logged = []
    moved = profiles.stash_els(els, "Cops", ["a.xml"], log=logged.append)
    assert moved == 1 and logged == [1]
    assert not (els / "pack_default" / "a.xml").exists()
    assert (els / "pack_default" / "b.xml").exists()  # not part of the profile
    assert (profiles.unused_dir(els, "Cops") / "a.xml").exists()


def test_stash_ignores_unknown_files_and_empty_input(tmp: Path):
    els = _els_root(tmp, "a.xml")
    assert profiles.stash_els(els, "Cops", ["nope.xml"]) == 0
    assert profiles.stash_els(els, "Cops", []) == 0
    assert profiles.stash_els(tmp / "missing", "Cops", ["a.xml"]) == 0
    assert not profiles.unused_dir(els, "Cops").exists()


def test_stash_does_not_touch_files_already_stashed(tmp: Path):
    els = _els_root(tmp)
    other = profiles.unused_dir(els, "Other")
    other.mkdir()
    (other / "a.xml").write_text("<vcf/>")
    assert profiles.stash_els(els, "Cops", ["a.xml"]) == 0
    assert (other / "a.xml").exists()


def test_restore_brings_files_back_and_removes_the_stash(tmp: Path):
    els = _els_root(tmp, "a.xml")
    profiles.stash_els(els, "Cops", ["a.xml"])
    logged = []
    assert profiles.restore_els(els, "Cops", log=logged.append) == 1
    assert logged == [1]
    assert (els / "pack_default" / "a.xml").exists()
    assert not profiles.unused_dir(els, "Cops").exists()


def test_restore_without_stash_does_nothing(tmp: Path):
    els = _els_root(tmp, "a.xml")
    assert profiles.restore_els(els, "Cops") == 0
    assert (els / "pack_default" / "a.xml").exists()


def test_restore_recreates_a_missing_live_folder(tmp: Path):
    els = _els_root(tmp, "a.xml")
    profiles.stash_els(els, "Cops", ["a.xml"])
    (els / "pack_default").rmdir()
    assert profiles.restore_els(els, "Cops") == 1
    assert (els / "pack_default" / "a.xml").exists()


def test_rename_stash_moves_the_folder(tmp: Path):
    els = _els_root(tmp, "a.xml")
    profiles.stash_els(els, "Cops", ["a.xml"])
    assert profiles.rename_stash(els, "Cops", "Police") is True
    assert not profiles.unused_dir(els, "Cops").exists()
    assert (profiles.unused_dir(els, "Police") / "a.xml").exists()
    # the renamed profile can now find its files again
    assert profiles.restore_els(els, "Police") == 1
    assert (els / "pack_default" / "a.xml").exists()


def test_rename_stash_merges_into_an_existing_stash(tmp: Path):
    els = _els_root(tmp, "a.xml", "b.xml")
    profiles.stash_els(els, "Cops", ["a.xml"])
    profiles.stash_els(els, "Police", ["b.xml"])
    assert profiles.rename_stash(els, "Cops", "Police") is True
    merged = profiles.unused_dir(els, "Police")
    assert sorted(p.name for p in merged.iterdir()) == ["a.xml", "b.xml"]
    assert not profiles.unused_dir(els, "Cops").exists()


def test_rename_stash_noop_cases(tmp: Path):
    els = _els_root(tmp, "a.xml")
    assert profiles.rename_stash(els, "Cops", "Police") is False  # nothing stashed
    profiles.stash_els(els, "Cops", ["a.xml"])
    assert profiles.rename_stash(els, "Cops", "Cops") is False
    assert profiles.rename_stash(els, "Cops", "cops") is False  # only the case changed
    assert (profiles.unused_dir(els, "Cops") / "a.xml").exists()


if __name__ == "__main__":
    raise SystemExit(run(globals()))
