"""Mod-installation logic per mod type.

Each installer takes a source `Path` (a dropped file or folder) and a
target directory, validates the source, then copies it into place. The
returned `InstallResult` carries a status flag, a human-readable message
and (for DLCs) the detected pack name so the GUI can update dlclist.xml.

When a target already exists, installers do **not** overwrite silently:
they return `conflict=True` so the GUI can ask the user whether to replace.
Calling again with `overwrite=True` then performs the replacement.

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
    conflict: bool = False


def find_dlc_packs(src: Path) -> list[Path]:
    """Return every DLC pack folder reachable from `src`.

    A DLC pack is a folder containing a `dlc.rpf` file. Accept either the
    pack folder itself or a wrapper folder one level up that contains one
    or more pack folders, so dropping a single archive folder with several
    addons installs all of them.
    """
    if not src.is_dir():
        return []
    if (src / "dlc.rpf").exists():
        return [src]
    try:
        children = [c for c in src.iterdir() if c.is_dir()]
    except OSError:
        return []
    return [c for c in children if (c / "dlc.rpf").exists()]


def install_dlc(
    pack: Path, dlcpacks_dir: Path, log: LogFn, overwrite: bool = False
) -> InstallResult:
    """Install a single, already-resolved DLC pack folder.

    Use `find_dlc_packs` first to turn a dropped path into pack folders.
    """
    target = dlcpacks_dir / pack.name
    if target.exists() and not overwrite:
        return InstallResult(
            False,
            T("dlc_exists", name=pack.name, dir=str(dlcpacks_dir)),
            pack.name,
            conflict=True,
        )
    log(T("dlc_copying", name=pack.name, dir=str(dlcpacks_dir)))
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(pack, target)
    except OSError as exc:
        # Clean up a half-copied folder so it isn't mistaken for a good install.
        if target.exists():
            shutil.rmtree(target, ignore_errors=True)
        return InstallResult(
            False, T("dlc_copy_failed", name=pack.name, err=str(exc)), pack.name
        )
    return InstallResult(True, T("dlc_installed", name=pack.name), pack.name)


def list_installed_dlcs(dlcpacks_dir: Path) -> list[str]:
    """Return the names of installed DLC packs (folders containing dlc.rpf)."""
    if not dlcpacks_dir.is_dir():
        return []
    try:
        children = [c for c in dlcpacks_dir.iterdir() if c.is_dir()]
    except OSError:
        return []
    return sorted(c.name for c in children if (c / "dlc.rpf").exists())


def uninstall_dlc(name: str, dlcpacks_dir: Path, log: LogFn) -> InstallResult:
    """Delete an installed DLC pack folder from `dlcpacks_dir`.

    Only removes the files on disk; the GUI is responsible for also dropping
    the matching `dlclist.xml` entry via `dlclist.remove_from_file`.
    """
    target = dlcpacks_dir / name
    if not target.is_dir():
        return InstallResult(False, T("dlc_not_installed", name=name), name)
    log(T("dlc_removing", name=name))
    try:
        shutil.rmtree(target)
    except OSError as exc:
        return InstallResult(
            False, T("dlc_remove_failed", name=name, err=str(exc)), name
        )
    return InstallResult(True, T("dlc_removed", name=name), name)


def _looks_like_els_xml(path: Path) -> bool:
    if path.suffix.lower() != ".xml":
        return False
    try:
        head = path.read_text(encoding="utf-8", errors="ignore")[:2048].lower()
    except OSError:
        return False
    return "<vcfroot" in head or "<vcf " in head or "<elsteam" in head


def install_els(
    src: Path, els_vcfs_dir: Path, log: LogFn, overwrite: bool = False
) -> InstallResult:
    if not src.exists():
        return InstallResult(False, T("els_src_missing", path=str(src)))

    try:
        els_vcfs_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return InstallResult(False, T("els_copy_failed", name=src.name, err=str(exc)))

    if src.is_file():
        if not _looks_like_els_xml(src):
            return InstallResult(False, T("els_not_vcf", name=src.name))
        target = els_vcfs_dir / src.name
        if target.exists() and not overwrite:
            return InstallResult(
                False, T("els_file_exists", name=target.name), conflict=True
            )
        log(T("els_copying_file", name=src.name))
        try:
            shutil.copy2(src, target)
        except OSError as exc:
            return InstallResult(
                False, T("els_copy_failed", name=src.name, err=str(exc))
            )
        return InstallResult(True, T("els_installed_file", name=src.name))

    xmls = [x for x in src.rglob("*.xml") if _looks_like_els_xml(x)]
    if not xmls:
        return InstallResult(False, T("els_no_xmls"))

    existing = [x for x in xmls if (els_vcfs_dir / x.name).exists()]
    if existing and not overwrite:
        return InstallResult(
            False, T("els_some_exist", count=len(existing)), conflict=True
        )

    copied = 0
    for x in xmls:
        log(T("els_copying", name=x.name))
        try:
            shutil.copy2(x, els_vcfs_dir / x.name)
        except OSError as exc:
            return InstallResult(
                False,
                T("els_copy_failed_partial", name=x.name, err=str(exc), copied=copied),
            )
        copied += 1
    return InstallResult(True, T("els_summary", copied=copied, skipped=0))
