from __future__ import annotations

import shutil
from pathlib import Path
from typing import Callable, Optional

LogFn = Callable[[int], None]

PACK_DEFAULT = "pack_default"
UNUSED_SUFFIX = " unused"


def safe_folder_name(name: str) -> str:
    cleaned = "".join(c for c in name if c.isalnum() or c in " _-").strip()
    return cleaned or "profile"


def unused_dir(els_root: Path, profile_name: str) -> Path:
    return els_root / (safe_folder_name(profile_name) + UNUSED_SUFFIX)


def _under_unused(path: Path, els_root: Path) -> bool:
    try:
        rel = path.relative_to(els_root)
    except ValueError:
        return True
    return any(p.lower().endswith(UNUSED_SUFFIX) for p in rel.parts[:-1])


def stash_els(
    els_root: Path,
    profile_name: str,
    file_names,
    log: Optional[LogFn] = None,
) -> int:
    if not els_root.is_dir() or not file_names:
        return 0
    wanted = set(file_names)
    moved = 0
    for name in wanted:
        for f in els_root.rglob(name):
            if not f.is_file() or _under_unused(f, els_root):
                continue
            dest.mkdir(parents=True, exist_ok=True)
            target = dest / f.name
            try:
                if target.exists():
                    target.unlink()
                shutil.move(str(f), str(target))
                moved += 1
            except OSError:
                pass
            break
    if moved and log:
        log(moved)
    return moved


def restore_els(
    els_root: Path,
    profile_name: str,
    log: Optional[LogFn] = None,
) -> int:
    src = unused_dir(els_root, profile_name)
    if not src.is_dir():
        return 0
    dest = els_root / PACK_DEFAULT
    dest.mkdir(parents=True, exist_ok=True)
    restored = 0
    for f in list(src.rglob("*")):
        if not f.is_file():
            continue
        target = dest / f.name
        try:
            if target.exists():
                target.unlink()
            shutil.move(str(f), str(target))
            restored += 1
        except OSError:
            pass
    shutil.rmtree(src, ignore_errors=True)
    if restored and log:
        log(restored)
    return restored
