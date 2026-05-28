"""Detect and validate GTA V install paths."""
from __future__ import annotations

from pathlib import Path
from typing import Optional


REQUIRED_MARKERS = ("GTA5.exe", "GTAVLauncher.exe", "PlayGTAV.exe")

TYPICAL_PATHS = (
    r"C:\Program Files\Rockstar Games\Grand Theft Auto V",
    r"C:\Program Files (x86)\Rockstar Games\Grand Theft Auto V",
    r"C:\Program Files (x86)\Steam\steamapps\common\Grand Theft Auto V",
    r"C:\Program Files\Steam\steamapps\common\Grand Theft Auto V",
    r"C:\Program Files\Epic Games\GTAV",
    r"D:\Games\Grand Theft Auto V",
)


def is_gta_root(path: Path) -> bool:
    if not path or not path.is_dir():
        return False
    return any((path / m).exists() for m in REQUIRED_MARKERS)


def find_default_install() -> Optional[Path]:
    for p in TYPICAL_PATHS:
        path = Path(p)
        if is_gta_root(path):
            return path
    return None


def derive_paths(gta_root: Path, use_mods: bool = True) -> dict:
    """Return important sub-paths used for modding.

    `use_mods=True` follows the OpenIV `mods/` folder convention, so the
    original game files stay untouched. dlcpacks then resolves to
    `<gta>/mods/update/x64/dlcpacks` instead of `<gta>/update/x64/dlcpacks`.
    """
    base = gta_root / "mods" if use_mods else gta_root
    return {
        "root": gta_root,
        "mods_root": base,
        "update_rpf": base / "update" / "update.rpf",
        "dlcpacks": base / "update" / "x64" / "dlcpacks",
        "dlclist_in_rpf_relative": "common/data/dlclist.xml",
        "els_root": gta_root / "ELS",
    }
