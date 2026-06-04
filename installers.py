from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from i18n import T


LogFn = Callable[[str], None]

ConflictResolver = Callable[[str], bool]

ProgressFn = Callable[[int, int, str], None]

_CHUNK = 4 * 1024 * 1024


@dataclass
class InstallResult:
    ok: bool
    message: str
    dlc_name: str = ""
    conflict: bool = False


def _iter_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file()]


def _human_size(num: int) -> str:
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
    dst.parent.mkdir(parents=True, exist_ok=True)
    name = src.name
    # copy in chunks so progress can update and the ui stays responsive on huge files
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
    if not src.is_dir():
        return []
    if (src / "dlc.rpf").exists():
        return [src]
    try:
        children = [c for c in src.iterdir() if c.is_dir()]
    except OSError:
        return []
    return [c for c in children if (c / "dlc.rpf").exists()]


def find_dlc_packs_deep(src: Path) -> list[Path]:
    if not src.is_dir():
        return []
    seen: set[Path] = set()
    packs: list[Path] = []
    for root, _dirs, files in os.walk(src):
        if any(name.lower() == "dlc.rpf" for name in files):
            folder = Path(root)
            if folder not in seen:
                seen.add(folder)
                packs.append(folder)
    return packs


def install_dlc(
    pack: Path,
    dlcpacks_dir: Path,
    log: LogFn,
    overwrite: bool = False,
    progress: Optional[ProgressFn] = None,
) -> InstallResult:
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
        # remove the half copied folder so it is not mistaken for a good install
        if target.exists():
            shutil.rmtree(target, ignore_errors=True)
        return InstallResult(
            False, T("dlc_copy_failed", name=pack.name, err=str(exc)), pack.name
        )
    return InstallResult(
        True, T("dlc_installed", name=pack.name, size=_human_size(total)), pack.name
    )


@dataclass
class InstalledDlc:
    name: str
    added: float


def list_installed_dlc_info(dlcpacks_dir: Path) -> list[InstalledDlc]:
    if not dlcpacks_dir.is_dir():
        return []
    try:
        children = [c for c in dlcpacks_dir.iterdir() if c.is_dir()]
    except OSError:
        return []
    out = []
    for c in children:
        if not (c / "dlc.rpf").exists():
            continue
        try:
            added = c.stat().st_ctime
        except OSError:
            added = 0.0
        out.append(InstalledDlc(c.name, added))
    return out


def list_installed_dlcs(dlcpacks_dir: Path) -> list[str]:
    return sorted(d.name for d in list_installed_dlc_info(dlcpacks_dir))


def uninstall_dlc(name: str, dlcpacks_dir: Path, log: LogFn) -> InstallResult:
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


_ELS_MARKERS = ("<vcf", "<elsteam", "<sirens", "<sirensettings")


def _looks_like_els_xml(path: Path) -> bool:
    if path.suffix.lower() != ".xml":
        return False
    try:
        head = path.read_text(encoding="utf-8", errors="ignore")[:8192].lower()
    except OSError:
        return False
    return any(marker in head for marker in _ELS_MARKERS)


def list_els_xmls(src: Path) -> list[Path]:
    if src.is_file():
        return [src] if _looks_like_els_xml(src) else []
    if src.is_dir():
        try:
            return [x for x in src.rglob("*.xml") if _looks_like_els_xml(x)]
        except OSError:
            return []
    return []


def group_els_by_folder(src: Path) -> dict[Path, list[Path]]:
    groups: dict[Path, list[Path]] = {}
    for xml in list_els_xmls(src):
        groups.setdefault(xml.parent, []).append(xml)
    return groups


def els_has_name_collision(groups: dict[Path, list[Path]]) -> bool:
    seen: dict[str, set[Path]] = {}
    for folder, files in groups.items():
        for f in files:
            seen.setdefault(f.name.lower(), set()).add(folder)
    return any(len(folders) > 1 for folders in seen.values())


def _path_distance(a: Path, b: Path) -> int:
    # folder steps between two paths up to the common ancestor then down
    ap, bp = a.parts, b.parts
    common = 0
    for x, y in zip(ap, bp):
        if x != y:
            break
        common += 1
    return (len(ap) - common) + (len(bp) - common)


def closest_els_folder(folders: list[Path], pack_folders: list[Path]) -> Path:
    if pack_folders:
        return min(
            folders,
            key=lambda f: (
                min(_path_distance(f, p) for p in pack_folders),
                len(f.parts),
                str(f).lower(),
            ),
        )
    return min(folders, key=lambda f: (len(f.parts), str(f).lower()))


def is_els_source(src: Path) -> bool:
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

    # resolve all conflicts first then copy so the total is exact and no dialog interrupts
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
