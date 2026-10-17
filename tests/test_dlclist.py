"""Unit tests for dlclist.py (editing the game's dlclist.xml as text).

Run with:  py -3 tests\\test_dlclist.py   — or —  py -3 -m pytest tests
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import dlclist
from _runner import run

XML = """<?xml version="1.0" encoding="UTF-8"?>
<SMandatoryPacksData>
  <Paths>
    <Item>dlcpacks:/alpha/</Item>
    <Item>dlcpacks:/beta/</Item>
    <Item>dlcpacks:/gamma/</Item>
  </Paths>
</SMandatoryPacksData>
"""


def test_list_entries():
    assert dlclist.list_entries(XML) == ["alpha", "beta", "gamma"]
    assert dlclist.list_active_entries(XML) == ["alpha", "beta", "gamma"]
    assert dlclist.list_disabled_entries(XML) == []


def test_add_entry_appends_with_matching_indent():
    out = dlclist.add_dlc_entry(XML, "delta")
    assert dlclist.list_entries(out) == ["alpha", "beta", "gamma", "delta"]
    assert "\n    <Item>dlcpacks:/delta/</Item>\n  </Paths>" in out


def test_add_entry_twice_changes_nothing():
    assert dlclist.add_dlc_entry(XML, "beta") == XML


def test_add_entry_needs_a_paths_block():
    try:
        dlclist.add_dlc_entry("<SMandatoryPacksData/>", "x")
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_disable_and_enable_roundtrip():
    off = dlclist.disable_dlc_entry(XML, "beta")
    assert dlclist.list_disabled_entries(off) == ["beta"]
    assert dlclist.list_active_entries(off) == ["alpha", "gamma"]
    assert dlclist.disable_dlc_entry(off, "beta") == off  # already disabled
    assert dlclist.enable_dlc_entry(off, "beta") == XML


def test_remove_entry_takes_the_whole_line():
    out = dlclist.remove_dlc_entry(XML, "beta")
    assert dlclist.list_entries(out) == ["alpha", "gamma"]
    assert "beta" not in out
    assert "\n\n" not in out  # no blank line left behind
    # a disabled entry is removed too
    off = dlclist.disable_dlc_entry(XML, "beta")
    assert "beta" not in dlclist.remove_dlc_entry(off, "beta")


def test_remove_does_not_confuse_similar_names():
    xml = dlclist.add_dlc_entry(XML, "alpha2")
    out = dlclist.remove_dlc_entry(xml, "alpha")
    assert dlclist.list_entries(out) == ["beta", "gamma", "alpha2"]


def test_move_entry():
    assert dlclist.list_ordered_entries(dlclist.move_entry(XML, "alpha", 1)) == ["beta", "alpha", "gamma"]
    # a longer step swaps the two entries, it does not shift the ones in between
    assert dlclist.list_ordered_entries(dlclist.move_entry(XML, "gamma", -2)) == ["gamma", "beta", "alpha"]
    assert dlclist.move_entry(XML, "alpha", -1) == XML  # already first
    assert dlclist.move_entry(XML, "gamma", 1) == XML   # already last
    assert dlclist.move_entry(XML, "missing", 1) == XML


def test_move_keeps_disabled_state():
    off = dlclist.disable_dlc_entry(XML, "alpha")
    out = dlclist.move_entry(off, "alpha", 1)
    assert dlclist.list_ordered_entries(out) == ["beta", "alpha", "gamma"]
    assert dlclist.list_disabled_entries(out) == ["alpha"]


def test_set_order():
    out = dlclist.set_order(XML, ["gamma", "alpha", "beta"])
    assert dlclist.list_ordered_entries(out) == ["gamma", "alpha", "beta"]
    # names not mentioned keep their relative order at the end
    out = dlclist.set_order(XML, ["gamma"])
    assert dlclist.list_ordered_entries(out) == ["gamma", "alpha", "beta"]
    assert dlclist.set_order(XML, ["alpha", "beta", "gamma"]) == XML


def test_duplicates_are_found_and_block_reordering():
    dup = dlclist.add_dlc_entry(XML, "alpha")  # no-op: add refuses duplicates
    assert dlclist.find_duplicate_entries(dup) == []
    dup = XML.replace("<Item>dlcpacks:/beta/</Item>", "<Item>dlcpacks:/alpha/</Item>")
    assert dlclist.find_duplicate_entries(dup) == ["alpha"]
    assert dlclist.set_order(dup, ["gamma", "alpha"]) == dup  # ambiguous -> untouched


def test_profile_block_hides_and_restores_entries():
    hidden = dlclist.comment_profile_block(XML, "p1", "Cops", ["alpha", "gamma"])
    assert dlclist.list_active_entries(hidden) == ["beta"]
    assert "ADDONV_START:p1" in hidden and "ADDONV_END:p1" in hidden
    assert "Profil: Cops" in hidden

    back = dlclist.uncomment_profile_block(hidden, "p1")
    assert "ADDONV" not in back
    assert sorted(dlclist.list_active_entries(back)) == ["alpha", "beta", "gamma"]


def test_profile_block_ignores_packs_that_are_not_installed():
    assert dlclist.comment_profile_block(XML, "p1", "Cops", ["nope"]) == XML
    assert dlclist.uncomment_profile_block(XML, "unknown") == XML


def test_two_profiles_dont_interfere():
    one = dlclist.comment_profile_block(XML, "p1", "One", ["alpha"])
    two = dlclist.comment_profile_block(one, "p2", "Two", ["beta"])
    assert dlclist.list_active_entries(two) == ["gamma"]
    back = dlclist.uncomment_profile_block(two, "p1")
    assert sorted(dlclist.list_active_entries(back)) == ["alpha", "gamma"]
    assert "ADDONV_START:p2" in back  # the other profile's block is still there


def test_file_edit_writes_a_backup_once(tmp: Path):
    xml = tmp / "dlclist.xml"
    xml.write_text(XML, encoding="utf-8")
    assert dlclist.update_file(xml, "delta") is True
    backup = tmp / "dlclist.xml.bak"
    assert backup.read_text(encoding="utf-8") == XML  # the untouched original
    assert dlclist.disable_in_file(xml, "alpha") is True
    assert backup.read_text(encoding="utf-8") == XML  # not overwritten by later edits
    assert dlclist.update_file(xml, "delta") is False  # nothing to change -> False
    text = xml.read_text(encoding="utf-8")
    assert dlclist.list_active_entries(text) == ["beta", "gamma", "delta"]
    assert dlclist.list_entries(text) == ["alpha", "beta", "gamma", "delta"]  # incl. disabled


if __name__ == "__main__":
    raise SystemExit(run(globals()))
