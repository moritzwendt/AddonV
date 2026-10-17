"""Backend-level tests: profiles and folder-mode switching against a fake GTA folder.

Every test runs with USERPROFILE/HOME pointed at a temp folder, so the real
~/.addonv/config.json is never read or written (Config.save() overwrites it).

Run with:  py -3 tests\\test_backend.py   — or —  py -3 -m pytest tests
"""
from __future__ import annotations

import importlib
import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _runner import run

DLCLIST = """<?xml version="1.0" encoding="UTF-8"?>
<SMandatoryPacksData>
  <Paths>
    <Item>dlcpacks:/alpha/</Item>
    <Item>dlcpacks:/beta/</Item>
  </Paths>
</SMandatoryPacksData>
"""

_ENV_KEYS = ("USERPROFILE", "HOME", "QT_QPA_PLATFORM")


@contextmanager
def sandboxed_backend(tmp: Path, **config_extra):
    """yield (backend, gta_folder) with an isolated config and a fake GTA install"""
    saved = {k: os.environ.get(k) for k in _ENV_KEYS}
    home = tmp / "home"
    (home / ".addonv").mkdir(parents=True)
    gta = tmp / "GTA"
    (gta / "ELS" / "pack_default").mkdir(parents=True)
    (gta / "GTA5.exe").write_bytes(b"")
    cfg = {"language": "de", "auto_check_updates": False,
           "save_terminal_history": False, "gta_path": str(gta)}
    cfg.update(config_extra)
    (home / ".addonv" / "config.json").write_text(json.dumps(cfg), encoding="utf-8")

    os.environ["USERPROFILE"] = os.environ["HOME"] = str(home)
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    import config
    import backend
    try:
        from PySide6.QtWidgets import QApplication
        QApplication.instance() or QApplication([])
        importlib.reload(config)
        importlib.reload(backend)
        assert str(config.CONFIG_FILE).startswith(str(home)), "config is not sandboxed!"
        b = backend.Backend()
        b._confirm = lambda *args, **kwargs: True  # no dialog window in tests
        yield b, gta
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        importlib.reload(config)
        importlib.reload(backend)


def _profile_ids(b) -> dict[str, str]:
    return {p["name"]: p["id"] for p in b.property("profiles")}


def _add_els(gta: Path, *names: str) -> None:
    for name in names:
        (gta / "ELS" / "pack_default" / name).write_text("<vcf/>")


def test_switching_profiles_hides_and_restores_els(tmp: Path):
    with sandboxed_backend(tmp) as (b, gta):
        _add_els(gta, "a.xml", "keep.xml")
        live = gta / "ELS" / "pack_default"
        b.saveProfile("Cops", [], ["a.xml"], "", "")
        b.saveProfile("Other", [], [], "", "")
        ids = _profile_ids(b)

        b.toggleProfile(ids["Cops"])
        assert b.property("activeProfile") == ids["Cops"]
        assert (live / "a.xml").exists()

        b.toggleProfile(ids["Other"])  # switching away hides Cops' files
        assert not (live / "a.xml").exists()
        assert (gta / "ELS" / "Cops unused" / "a.xml").exists()
        assert (live / "keep.xml").exists()  # not part of any profile

        b.toggleProfile(ids["Cops"])  # and switching back returns them
        assert (live / "a.xml").exists()
        assert not (gta / "ELS" / "Cops unused").exists()

        b.toggleProfile(ids["Cops"])  # clicking the active profile switches it off
        assert b.property("activeProfile") == ""
        assert not (live / "a.xml").exists()


def test_dlc_entries_follow_the_active_profile(tmp: Path):
    xml = tmp / "dlclist.xml"
    xml.write_text(DLCLIST, encoding="utf-8")
    with sandboxed_backend(tmp, dlclist_xml_path=str(xml)) as (b, gta):
        import dlclist
        b.saveProfile("Cops", ["alpha"], [], "", "")
        b.saveProfile("Other", [], [], "", "")
        ids = _profile_ids(b)

        b.toggleProfile(ids["Cops"])
        b.toggleProfile(ids["Other"])  # Cops is off -> alpha commented out
        text = xml.read_text(encoding="utf-8")
        assert dlclist.list_active_entries(text) == ["beta"]

        b.toggleProfile(ids["Cops"])
        text = xml.read_text(encoding="utf-8")
        assert sorted(dlclist.list_active_entries(text)) == ["alpha", "beta"]
        assert "ADDONV" not in text


def test_renaming_an_inactive_profile_keeps_its_hidden_files(tmp: Path):
    with sandboxed_backend(tmp) as (b, gta):
        _add_els(gta, "a.xml")
        b.saveProfile("Cops", [], ["a.xml"], "", "")
        b.saveProfile("Other", [], [], "", "")
        ids = _profile_ids(b)
        b.toggleProfile(ids["Cops"])
        b.toggleProfile(ids["Other"])
        assert (gta / "ELS" / "Cops unused" / "a.xml").exists()

        b.saveProfile("Police", [], ["a.xml"], "", ids["Cops"])  # rename
        assert not (gta / "ELS" / "Cops unused").exists()
        assert (gta / "ELS" / "Police unused" / "a.xml").exists()

        b.toggleProfile(ids["Cops"])  # the renamed profile finds its file again
        assert (gta / "ELS" / "pack_default" / "a.xml").exists()
        assert not (gta / "ELS" / "Police unused").exists()


def test_deleting_a_profile_gives_its_hidden_files_back(tmp: Path):
    with sandboxed_backend(tmp) as (b, gta):
        _add_els(gta, "a.xml")
        b.saveProfile("Cops", [], ["a.xml"], "", "")
        b.saveProfile("Other", [], [], "", "")
        ids = _profile_ids(b)
        b.toggleProfile(ids["Cops"])
        b.toggleProfile(ids["Other"])
        assert not (gta / "ELS" / "pack_default" / "a.xml").exists()

        b.deleteProfile(ids["Cops"])
        assert (gta / "ELS" / "pack_default" / "a.xml").exists()
        assert "Cops" not in _profile_ids(b)


def test_switching_between_mods_and_direct_folder_rescans(tmp: Path):
    with sandboxed_backend(tmp) as (b, gta):
        for base, name in ((gta / "mods", "InModsFolder"), (gta, "InGameFolder")):
            d = base / "update" / "x64" / "dlcpacks" / name
            d.mkdir(parents=True)
            (d / "dlc.rpf").write_text("x")
        names = lambda: [p["name"] for p in b.property("packs")]

        b.reloadMods()
        assert names() == ["InModsFolder"]
        assert b.setUseModsFolder(False) is True
        assert names() == ["InGameFolder"]  # list follows the new folder at once
        assert b.setUseModsFolder(True) is True
        assert names() == ["InModsFolder"]


def test_declining_the_direct_mode_warning_changes_nothing(tmp: Path):
    with sandboxed_backend(tmp) as (b, gta):
        d = gta / "mods" / "update" / "x64" / "dlcpacks" / "InModsFolder"
        d.mkdir(parents=True)
        (d / "dlc.rpf").write_text("x")
        b.reloadMods()
        b._confirm = lambda *args, **kwargs: False
        assert b.setUseModsFolder(False) is False
        assert b.property("useModsFolder") is True
        assert [p["name"] for p in b.property("packs")] == ["InModsFolder"]


if __name__ == "__main__":
    raise SystemExit(run(globals()))
