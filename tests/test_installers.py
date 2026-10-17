"""Unit tests for installers.py (DLC / ELS / custom-zone copying).

Run with:  py -3 tests\\test_installers.py   — or —  py -3 -m pytest tests
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import installers
from _runner import run

LOG = lambda msg: None


def _pack(root: Path, name: str, tag: str, extra=()) -> Path:
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "dlc.rpf").write_text(tag)
    for e in extra:
        (d / e).write_text(tag)
    return d


def _folders(path: Path) -> list[str]:
    return sorted(p.name for p in path.iterdir())


def test_find_dlc_packs(tmp: Path):
    single = _pack(tmp, "single", "x")
    assert installers.find_dlc_packs(single) == [single]
    parent = tmp / "many"
    a = _pack(parent, "a", "x")
    b = _pack(parent, "b", "x")
    (parent / "junk").mkdir()
    assert sorted(installers.find_dlc_packs(parent)) == [a, b]
    assert installers.find_dlc_packs(tmp / "missing") == []


def test_find_dlc_packs_deep_is_case_insensitive(tmp: Path):
    deep = tmp / "outer" / "inner" / "pack"
    deep.mkdir(parents=True)
    (deep / "DLC.RPF").write_text("x")
    assert installers.find_dlc_packs_deep(tmp / "outer") == [deep]


def test_install_dlc_fresh(tmp: Path):
    dlcpacks = tmp / "dlcpacks"
    dlcpacks.mkdir()
    src = _pack(tmp / "src", "pack", "NEW", ["a.bin"])
    result = installers.install_dlc(src, dlcpacks, LOG)
    assert result.ok and not result.conflict and result.dlc_name == "pack"
    assert (dlcpacks / "pack" / "dlc.rpf").read_text() == "NEW"
    assert (dlcpacks / "pack" / "a.bin").exists()
    assert _folders(dlcpacks) == ["pack"]


def test_install_dlc_reports_conflict_and_keeps_the_old_pack(tmp: Path):
    dlcpacks = tmp / "dlcpacks"
    _pack(dlcpacks, "pack", "OLD")
    src = _pack(tmp / "src", "pack", "NEW")
    result = installers.install_dlc(src, dlcpacks, LOG)
    assert not result.ok and result.conflict
    assert (dlcpacks / "pack" / "dlc.rpf").read_text() == "OLD"


def test_install_dlc_overwrite_replaces_content_and_leaves_no_temp_folders(tmp: Path):
    dlcpacks = tmp / "dlcpacks"
    _pack(dlcpacks, "pack", "OLD", ["old_only.bin"])
    src = _pack(tmp / "src", "pack", "NEW", ["new_only.bin"])
    result = installers.install_dlc(src, dlcpacks, LOG, overwrite=True)
    assert result.ok
    assert (dlcpacks / "pack" / "dlc.rpf").read_text() == "NEW"
    assert not (dlcpacks / "pack" / "old_only.bin").exists()  # replaced, not merged
    assert (dlcpacks / "pack" / "new_only.bin").exists()
    assert _folders(dlcpacks) == ["pack"]


def test_failed_copy_keeps_the_old_pack(tmp: Path):
    dlcpacks = tmp / "dlcpacks"
    _pack(dlcpacks, "pack", "OLD", ["old.bin"])
    src = _pack(tmp / "src", "pack", "NEW", ["x.bin", "y.bin"])

    real, calls = installers._copy_file, {"n": 0}

    def flaky(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 2:
            raise OSError("disk full (simulated)")
        return real(*args, **kwargs)

    installers._copy_file = flaky
    try:
        result = installers.install_dlc(src, dlcpacks, LOG, overwrite=True)
    finally:
        installers._copy_file = real

    assert not result.ok
    assert (dlcpacks / "pack" / "dlc.rpf").read_text() == "OLD"
    assert (dlcpacks / "pack" / "old.bin").exists()
    assert _folders(dlcpacks) == ["pack"]  # half-copied staging folder is gone


def test_failed_fresh_install_leaves_nothing_behind(tmp: Path):
    dlcpacks = tmp / "dlcpacks"
    dlcpacks.mkdir()
    src = _pack(tmp / "src", "pack", "NEW", ["x.bin"])

    real = installers._copy_file

    def always_fail(*args, **kwargs):
        raise OSError("locked (simulated)")

    installers._copy_file = always_fail
    try:
        result = installers.install_dlc(src, dlcpacks, LOG)
    finally:
        installers._copy_file = real

    assert not result.ok
    assert _folders(dlcpacks) == []


def test_swap_failure_puts_the_old_pack_back(tmp: Path):
    dlcpacks = tmp / "dlcpacks"
    _pack(dlcpacks, "pack", "OLD")
    missing_staging = dlcpacks / "pack.addonv-new"  # never created -> rename fails
    try:
        installers._swap_in(missing_staging, dlcpacks / "pack", dlcpacks / "pack.addonv-old")
    except OSError:
        pass
    else:
        raise AssertionError("expected the swap to fail")
    assert (dlcpacks / "pack" / "dlc.rpf").read_text() == "OLD"
    assert _folders(dlcpacks) == ["pack"]


def test_replacing_a_pack_with_its_own_folder_does_not_delete_it(tmp: Path):
    # dragging the installed folder onto the app and answering "replace" used to
    # delete the pack before it could be copied from itself
    dlcpacks = tmp / "dlcpacks"
    installed = _pack(dlcpacks, "pack", "KEEP", ["a.bin"])
    result = installers.install_dlc(installed, dlcpacks, LOG, overwrite=True)
    assert result.ok
    assert (dlcpacks / "pack" / "dlc.rpf").read_text() == "KEEP"
    assert (dlcpacks / "pack" / "a.bin").exists()
    assert _folders(dlcpacks) == ["pack"]


def test_leftover_staging_folders_are_hidden_and_cleaned_up(tmp: Path):
    dlcpacks = tmp / "dlcpacks"
    _pack(dlcpacks, "pack", "OLD")
    _pack(dlcpacks, "pack.addonv-new", "stale")
    _pack(dlcpacks, "pack.addonv-old", "stale")
    assert installers.list_installed_dlcs(dlcpacks) == ["pack"]
    src = _pack(tmp / "src", "pack", "NEW")
    assert installers.install_dlc(src, dlcpacks, LOG, overwrite=True).ok
    assert _folders(dlcpacks) == ["pack"]
    assert (dlcpacks / "pack" / "dlc.rpf").read_text() == "NEW"


def test_uninstall_dlc(tmp: Path):
    dlcpacks = tmp / "dlcpacks"
    _pack(dlcpacks, "pack", "x")
    assert installers.uninstall_dlc("pack", dlcpacks, LOG).ok
    assert _folders(dlcpacks) == []
    assert not installers.uninstall_dlc("pack", dlcpacks, LOG).ok  # already gone


def test_install_path_copies_files_and_folders(tmp: Path):
    target = tmp / "scripts"
    f = tmp / "src" / "one.asi"
    f.parent.mkdir()
    f.write_text("A")
    d = tmp / "src" / "folder"
    (d / "sub").mkdir(parents=True)
    (d / "sub" / "two.txt").write_text("B")
    assert installers.install_path(f, target, LOG).ok
    assert installers.install_path(d, target, LOG).ok
    assert (target / "one.asi").read_text() == "A"
    assert (target / "folder" / "sub" / "two.txt").read_text() == "B"
    again = installers.install_path(f, target, LOG)
    assert not again.ok and again.conflict


def test_els_detection_and_install_with_conflict_resolution(tmp: Path):
    src = tmp / "src"
    src.mkdir()
    (src / "police.xml").write_text("<vcfroot><sirens/></vcfroot>")
    (src / "readme.xml").write_text("<notes>hello</notes>")  # not an ELS file
    assert installers.is_els_source(src)
    assert [p.name for p in installers.list_els_xmls(src)] == ["police.xml"]

    target = tmp / "ELS" / "pack_default"
    first = installers.install_els(src, target, LOG)
    assert first.ok and (target / "police.xml").exists()
    assert not (target / "readme.xml").exists()

    (target / "police.xml").write_text("OLD")
    kept = installers.install_els(src, target, LOG, resolve=lambda name: False)
    assert kept.ok and (target / "police.xml").read_text() == "OLD"
    replaced = installers.install_els(src, target, LOG, resolve=lambda name: True)
    assert replaced.ok and (target / "police.xml").read_text() != "OLD"


def test_els_install_rejects_non_els_input(tmp: Path):
    plain = tmp / "plain.xml"
    plain.write_text("<notes/>")
    assert not installers.install_els(plain, tmp / "out", LOG).ok
    assert not installers.install_els(tmp / "missing", tmp / "out", LOG).ok
    empty = tmp / "empty"
    empty.mkdir()
    assert not installers.install_els(empty, tmp / "out", LOG).ok


def test_group_els_by_install_time():
    def f(name, mtime):
        return installers.InstalledEls(Path(name), name, mtime)

    groups = installers.group_els_by_install_time(
        [f("a.xml", 100.0), f("b.xml", 100.5), f("c.xml", 500.0)]
    )
    assert [[x.name for x in g] for g in groups] == [["a.xml", "b.xml"], ["c.xml"]]


def test_derive_group_name():
    assert installers.derive_group_name([]) == ""
    assert installers.derive_group_name(["police.xml"]) == "police"
    # a shared prefix is cut back to a whole word, trailing numbers are dropped
    assert installers.derive_group_name(["lspd_car1.xml", "lspd_car2.xml"]) == "lspd"
    assert installers.derive_group_name(["SheriffCar.xml", "SheriffVan.xml"]) == "Sheriff"
    assert installers.derive_group_name(["mypack_1.xml", "mypack_2.xml"]) == "mypack"
    assert installers.derive_group_name(["abc1.xml", "xyz2.xml"]) == ""  # nothing in common


if __name__ == "__main__":
    raise SystemExit(run(globals()))
