"""Mod-installation logic per mod type.

Each installer takes a source `Path` (a dropped file or folder) and a
target directory, validates the source, then copies it into place. The
returned `InstallResult` carries a status flag, a human-readable message
and (for DLCs) the detected pack name so the GUI can update dlclist.xml.

User-facing strings are looked up via `i18n.T` so messages follow the
current language.
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from i18n import T


LogFn = Callable[[str], None]


@dataclass
class InstallResult:
    ok: bool
    message: str
    dlc_name: str = ""


def _find_dlc_folder(src: Path) -> Optional[Path]:
    """A DLC pack is a folder containing a `dlc.rpf` file.

    Accept either the pack folder itself or a wrapper folder one level up.
    """
    if not src.is_dir():
        return None
    if (src / "dlc.rpf").exists():
        return src
    try:
        children = [c for c in src.iterdir() if c.is_dir()]
    except OSError:
        return None
    candidates = [c for c in children if (c / "dlc.rpf").exists()]
    if len(candidates) == 1:
        return candidates[0]
    return None


def install_dlc(src: Path, dlcpacks_dir: Path, log: LogFn) -> InstallResult:
    dlc = _find_dlc_folder(src)
    if not dlc:
        return InstallResult(False, T("dlc_no_rpf", name=src.name))
    target = dlcpacks_dir / dlc.name
    if target.exists():
        return InstallResult(
            False,
            T("dlc_exists", name=dlc.name, dir=str(dlcpacks_dir)),
            dlc.name,
        )
    log(T("dlc_copying", name=dlc.name, dir=str(dlcpacks_dir)))
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(dlc, target)
    return InstallResult(True, T("dlc_installed", name=dlc.name), dlc.name)


def _looks_like_els_xml(path: Path) -> bool:
    if path.suffix.lower() != ".xml":
        return False
    try:
        head = path.read_text(encoding="utf-8", errors="ignore")[:2048].lower()
    except OSError:
        return False
    return "<vcfroot" in head or "<vcf " in head or "<elsteam" in head


def install_els(src: Path, els_vcfs_dir: Path, log: LogFn) -> InstallResult:
    if not src.exists():
        return InstallResult(False, T("els_src_missing", path=str(src)))

    els_vcfs_dir.mkdir(parents=True, exist_ok=True)

    if src.is_file():
        if not _looks_like_els_xml(src):
            return InstallResult(False, T("els_not_vcf", name=src.name))
        target = els_vcfs_dir / src.name
        if target.exists():
            return InstallResult(False, T("els_file_exists", name=target.name))
        log(T("els_copying_file", name=src.name))
        shutil.copy2(src, target)
        return InstallResult(True, T("els_installed_file", name=src.name))

    xmls = [x for x in src.rglob("*.xml") if _looks_like_els_xml(x)]
    if not xmls:
        return InstallResult(False, T("els_no_xmls"))

    copied = skipped = 0
    for x in xmls:
        target = els_vcfs_dir / x.name
        if target.exists():
            log(T("els_skipped", name=target.name))
            skipped += 1
            continue
        log(T("els_copying", name=x.name))
        shutil.copy2(x, target)
        copied += 1
    return InstallResult(True, T("els_summary", copied=copied, skipped=skipped))
