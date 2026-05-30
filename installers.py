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

# Given the name of an item that already exists at the target, return True to
# replace it or False to keep the existing one. Lets the caller (the GUI) ask
# the user per item, with "yes/no to all" handled inside the resolver.
ConflictResolver = Callable[[str], bool]

# Reports copy progress: (bytes_done, bytes_total, current_file_name). Called
# repeatedly during a copy so the GUI can animate a progress bar and keep the
# event loop alive. Receiving a total of 0 means "nothing to copy".
ProgressFn = Callable[[int, int, str], None]

_CHUNK = 4 * 1024 * 1024  # 4 MiB copy block — small enough to keep the UI live


@dataclass
class InstallResult:
    ok: bool
    message: str
    dlc_name: str = ""
    conflict: bool = False


def _iter_files(root: Path) -> list[Path]:
    """All files under `root`, recursively (no directories)."""
    return [p for p in root.rglob("*") if p.is_file()]


def _human_size(num: int) -> str:
    """Format a byte count compactly, e.g. 1536 -> '1.5 KB'."""
    size = float(num)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{int(size)} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def _copy_file(
    src: Path,
    dst: Path,
    done: int,
    total: int,
    progress: Optional[ProgressFn],
) -> int:
    """Copy `src` to `dst` in chunks, reporting cumulative progress.

    `done` is the byte count copied before this file; returns the new
    cumulative count afterwards. Copying in chunks (rather than one big
    `copy2`) lets the caller pump its event loop between blocks so even a
    single huge file doesn't freeze the UI.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    name = src.name
    with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
        while True:
            chunk = fsrc.read(_CHUNK)
            if not chunk:
                break
            fdst.write(chunk)
            done += len(chunk)
            if progress is not None:
                progress(done, total, name)
    shutil.copymode(src, dst)
    return done


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
    pack: Path,
    dlcpacks_dir: Path,
    log: LogFn,
    overwrite: bool = False,
    progress: Optional[ProgressFn] = None,
) -> InstallResult:
    """Install a single, already-resolved DLC pack folder.

    Use `find_dlc_packs` first to turn a dropped path into pack folders.
    Copies file-by-file (reporting `progress`) instead of one opaque
    `copytree`, so the GUI can show a live progress bar.
    """
    target = dlcpacks_dir / pack.name
    if target.exists() and not overwrite:
        return InstallResult(
            False,
            T("dlc_exists", name=pack.name, dir=str(dlcpacks_dir)),
            pack.name,
            conflict=True,
        )
    log(T("dlc_installing", name=pack.name))
    try:
        files = _iter_files(pack)
        total = sum(f.stat().st_size for f in files)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            shutil.rmtree(target)
        done = 0
        if progress is not None:
            progress(0, total, pack.name)
        for f in files:
            rel = f.relative_to(pack)
            done = _copy_file(f, target / rel, done, total, progress)
    except OSError as exc:
        # Clean up a half-copied folder so it isn't mistaken for a good install.
        if target.exists():
            shutil.rmtree(target, ignore_errors=True)
        return InstallResult(
            False, T("dlc_copy_failed", name=pack.name, err=str(exc)), pack.name
        )
    return InstallResult(
        True, T("dlc_installed", name=pack.name, size=_human_size(total)), pack.name
    )


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


def list_els_xmls(src: Path) -> list[Path]:
    """Return every ELS-VCF XML file reachable from `src` (file or folder)."""
    if src.is_file():
        return [src] if _looks_like_els_xml(src) else []
    if src.is_dir():
        try:
            return [x for x in src.rglob("*.xml") if _looks_like_els_xml(x)]
        except OSError:
            return []
    return []


def is_els_source(src: Path) -> bool:
    """True if `src` is an ELS-VCF XML file or a folder that contains one.

    Lets the GUI auto-route a dropped path: anything that isn't a DLC pack
    but looks like ELS goes to the ELS installer.
    """
    if src.is_file():
        return _looks_like_els_xml(src)
    if src.is_dir():
        try:
            return any(_looks_like_els_xml(x) for x in src.rglob("*.xml"))
        except OSError:
            return False
    return False


def install_els(
    src: Path,
    els_vcfs_dir: Path,
    log: LogFn,
    resolve: Optional[ConflictResolver] = None,
    progress: Optional[ProgressFn] = None,
) -> InstallResult:
    """Install one or more ELS-VCF XML files into `els_vcfs_dir`.

    Conflicts are resolved up front (via `resolve(name)`, with "yes/no to all"
    handled inside the resolver); files the user keeps are skipped. The
    remaining files are then copied while reporting `progress`.
    """
    if not src.exists():
        return InstallResult(False, T("els_src_missing", path=str(src)))

    try:
        els_vcfs_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return InstallResult(False, T("els_copy_failed", name=src.name, err=str(exc)))

    if src.is_file():
        if not _looks_like_els_xml(src):
            return InstallResult(False, T("els_not_vcf", name=src.name))
        xmls = [src]
    else:
        xmls = [x for x in src.rglob("*.xml") if _looks_like_els_xml(x)]
        if not xmls:
            return InstallResult(False, T("els_no_xmls"))

    # Decide everything first, then copy — keeps the byte total exact and the
    # progress bar smooth (no dialogs interrupting the copy phase).
    to_copy = []
    skipped = 0
    for x in xmls:
        target = els_vcfs_dir / x.name
        if target.exists() and not (resolve is not None and resolve(x.name)):
            skipped += 1
            continue
        to_copy.append(x)

    total = sum(x.stat().st_size for x in to_copy)
    done = 0
    if progress is not None:
        progress(0, total, src.name)
    for x in to_copy:
        try:
            done = _copy_file(x, els_vcfs_dir / x.name, done, total, progress)
        except OSError as exc:
            return InstallResult(
                False,
                T(
                    "els_copy_failed_partial",
                    name=x.name,
                    err=str(exc),
                    copied=to_copy.index(x),
                ),
            )
    return InstallResult(
        True, T("els_summary", copied=len(to_copy), skipped=skipped)
    )
