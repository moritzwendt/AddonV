from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path


ARCHIVE_SUFFIXES = {".zip", ".oiv", ".7z", ".rar"}


class ArchiveError(Exception):
    pass


class UnsupportedArchive(ArchiveError):
    pass


class CorruptArchive(ArchiveError):
    pass


def is_archive(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in ARCHIVE_SUFFIXES


def extract_to_temp(path: Path) -> Path:
    tmp_root = Path(tempfile.mkdtemp(prefix="addonv_"))
    # extract into a folder named after the archive
    # so a pack file at the archive root gets named after the archive
    dest = tmp_root / path.stem
    dest.mkdir(parents=True, exist_ok=True)
    _extract(path, dest)
    return dest


def _sniff(path: Path) -> str | None:
    # identify the real format from magic bytes so a mislabelled archive still opens
    try:
        with open(path, "rb") as f:
            head = f.read(8)
    except OSError as exc:
        raise CorruptArchive(str(exc)) from exc
    if head[:4] in (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"):
        return "zip"
    if head[:6] == b"7z\xbc\xaf\x27\x1c":
        return "7z"
    if head[:4] == b"Rar!":
        return "rar"
    return None


def _extract(path: Path, dest: Path) -> None:
    fmt = _sniff(path)
    if fmt is None:
        suffix = path.suffix.lower()
        fmt = "zip" if suffix in (".zip", ".oiv") else suffix.lstrip(".")

    primary = {"zip": _unzip, "7z": _un7z, "rar": _unrar}.get(fmt)
    corrupt: CorruptArchive | None = None

    if primary is not None:
        try:
            primary(path, dest)
            return
        except CorruptArchive as exc:
            corrupt = exc
        except UnsupportedArchive:
            pass

    # fall back to a locally installed 7-zip which opens almost anything
    # like rar without a python backend or exotic zip compression
    seven_zip = _find_7z()
    if seven_zip is not None:
        _un_7zip(seven_zip, path, dest)
        return

    if corrupt is not None:
        raise corrupt
    raise UnsupportedArchive(fmt or path.suffix.lstrip("."))


def _unzip(path: Path, dest: Path) -> None:
    try:
        with zipfile.ZipFile(path) as zf:
            bad = zf.testzip()
            if bad is not None:
                raise CorruptArchive(f"bad CRC in {bad}")
            zf.extractall(dest)
    except zipfile.BadZipFile as exc:
        raise CorruptArchive(str(exc)) from exc
    except NotImplementedError as exc:
        raise UnsupportedArchive("zip") from exc


def _un7z(path: Path, dest: Path) -> None:
    try:
        import py7zr
    except ImportError as exc:
        raise UnsupportedArchive("7z") from exc
    try:
        with py7zr.SevenZipFile(path, mode="r") as zf:
            zf.extractall(path=dest)
    except Exception as exc:
        raise CorruptArchive(str(exc)) from exc


def _unrar(path: Path, dest: Path) -> None:
    try:
        import rarfile
    except ImportError as exc:
        raise UnsupportedArchive("rar") from exc
    try:
        with rarfile.RarFile(path) as rf:
            rf.extractall(dest)
    except rarfile.RarCannotExec as exc:
        raise UnsupportedArchive("rar") from exc
    except rarfile.Error as exc:
        raise CorruptArchive(str(exc)) from exc


def _find_7z() -> str | None:
    for name in ("7z", "7za", "7zr"):
        found = shutil.which(name)
        if found:
            return found
    for fixed in (
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe",
    ):
        if os.path.exists(fixed):
            return fixed
    return None


def _un_7zip(exe: str, path: Path, dest: Path) -> None:
    flags = 0
    if os.name == "nt":
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        proc = subprocess.run(
            [exe, "x", str(path), f"-o{dest}", "-y"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=flags,
        )
    except OSError as exc:
        raise ArchiveError(str(exc)) from exc
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or b"").decode("utf-8", "ignore").strip()
        raise CorruptArchive(detail or f"7-Zip exited with {proc.returncode}")
