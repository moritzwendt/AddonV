"""Unit tests for config.py (saving/loading ~/.addonv/config.json safely).

CONFIG_FILE is pointed at a temp folder for every test, so the real config is
never touched.

Run with:  py -3 tests\\test_config.py   — or —  py -3 -m pytest tests
"""
from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from _runner import run


@contextmanager
def config_at(path: Path):
    real = config.CONFIG_FILE
    config.CONFIG_FILE = path
    try:
        yield path
    finally:
        config.CONFIG_FILE = real


def _names(folder: Path) -> list[str]:
    return sorted(p.name for p in folder.iterdir())


def test_save_and_load_roundtrip(tmp: Path):
    with config_at(tmp / "sub" / "config.json") as f:
        cfg = config.Config()
        cfg.gta_path = r"F:\Games\GTA V"
        cfg.profiles = [{"id": "1", "name": "Ünïcode ✓", "dlc": ["a"], "els": []}]
        cfg.save()
        assert _names(f.parent) == ["config.json"]  # no temp file left behind
        loaded = config.Config.load()
        assert loaded.gta_path == r"F:\Games\GTA V"
        assert loaded.profiles == cfg.profiles
        assert loaded.broken_copy == ""


def test_missing_file_gives_defaults_and_creates_nothing(tmp: Path):
    with config_at(tmp / "config.json"):
        cfg = config.Config.load()
        assert cfg.language == "" and cfg.use_mods_folder is True
        assert cfg.broken_copy == ""
        assert _names(tmp) == []


def test_unknown_keys_in_the_file_are_ignored(tmp: Path):
    with config_at(tmp / "config.json") as f:
        f.write_text(json.dumps({"language": "de", "from_a_newer_version": 1}))
        assert config.Config.load().language == "de"


def test_crash_while_saving_keeps_the_old_file(tmp: Path):
    with config_at(tmp / "config.json") as f:
        old = config.Config()
        old.gta_path = "OLD-PATH"
        old.save()
        before = f.read_text(encoding="utf-8")

        class Boom(Exception):
            pass

        real_fsync = config.os.fsync
        seen = {}

        def dies_midway(fd):
            # the new content is written, the swap has not happened yet: this is
            # the moment a crash or power loss would hit
            seen["real_file_at_crash"] = f.read_text(encoding="utf-8")
            raise Boom("simulated crash while writing")

        config.os.fsync = dies_midway
        try:
            new = config.Config()
            new.gta_path = "NEW-PATH"
            try:
                new.save()
            except Boom:
                pass
            else:
                raise AssertionError("expected the simulated crash")
        finally:
            config.os.fsync = real_fsync

        assert seen["real_file_at_crash"] == before  # never half-written
        assert f.read_text(encoding="utf-8") == before  # untouched
        assert config.Config.load().gta_path == "OLD-PATH"
        assert _names(tmp) == ["config.json"]  # the half-written temp file is gone


def test_failed_swap_keeps_the_old_file_and_cleans_up(tmp: Path):
    with config_at(tmp / "config.json") as f:
        old = config.Config()
        old.gta_path = "OLD-PATH"
        old.save()

        real_replace = config.os.replace

        def refuse(src, dst):
            raise OSError("disk error (simulated)")

        config.os.replace = refuse
        try:
            new = config.Config()
            new.gta_path = "NEW-PATH"
            try:
                new.save()
            except OSError:
                pass
            else:
                raise AssertionError("expected the failed swap to raise")
        finally:
            config.os.replace = real_replace

        assert config.Config.load().gta_path == "OLD-PATH"
        assert _names(tmp) == ["config.json"]


def test_swap_is_retried_when_the_file_is_briefly_locked(tmp: Path):
    with config_at(tmp / "config.json"):
        real_replace = config.os.replace
        calls = {"n": 0}

        def locked_twice(src, dst):
            calls["n"] += 1
            if calls["n"] <= 2:
                raise PermissionError("in use by another process (simulated)")
            return real_replace(src, dst)

        config.os.replace = locked_twice
        try:
            cfg = config.Config()
            cfg.gta_path = "SAVED"
            cfg.save()
        finally:
            config.os.replace = real_replace

        assert calls["n"] == 3
        assert config.Config.load().gta_path == "SAVED"


def test_corrupt_file_is_set_aside_not_overwritten(tmp: Path):
    with config_at(tmp / "config.json") as f:
        f.write_text('{"gta_path": "F:\\\\Games", "profiles": [ {"id": ', encoding="utf-8")
        original = f.read_text(encoding="utf-8")

        cfg = config.Config.load()
        assert cfg.gta_path == ""  # defaults
        assert cfg.broken_copy == str(tmp / "config.json.broken")
        assert (tmp / "config.json.broken").read_text(encoding="utf-8") == original
        assert not f.exists()

        cfg.gta_path = "FRESH"
        cfg.save()  # a normal save afterwards must not destroy the broken copy
        assert (tmp / "config.json.broken").read_text(encoding="utf-8") == original
        reloaded = config.Config.load()
        assert reloaded.gta_path == "FRESH" and reloaded.broken_copy == ""


def test_valid_json_of_the_wrong_shape_counts_as_corrupt(tmp: Path):
    with config_at(tmp / "config.json") as f:
        f.write_text("[1, 2, 3]", encoding="utf-8")
        cfg = config.Config.load()
        assert cfg.broken_copy.endswith("config.json.broken")
        assert not f.exists()


def test_broken_copy_is_never_written_to_the_config_file(tmp: Path):
    with config_at(tmp / "config.json") as f:
        cfg = config.Config()
        cfg.broken_copy = "something"
        cfg.save()
        assert "broken_copy" not in json.loads(f.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(run(globals()))
