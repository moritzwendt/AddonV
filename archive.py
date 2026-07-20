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
    try:
        dest = tmp_root / path.stem
        dest.mkdir(parents=True, exist_ok=True)
        _extract(path, dest)
    except BaseException:
        # a failed/corrupt archive must not leave the temp dir behind
        shutil.rmtree(tmp_root, ignore_errors=True)
        raise
    return dest


def _sniff(path: Path) -> str | None:
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


def _reject_traversal(dest: Path, names) -> None:
    # zip-slip guard: refuse entries that resolve outside dest
    # (absolute paths, drive letters, or ../ escapes)
    base = dest.resolve()
    for name in names:
        if not name:
            continue
        target = (dest / name).resolve()
        if target == base or base in target.parents:
            continue
        raise CorruptArchive(f"unsafe path in archive: {name}")


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

    seven_zip = _find_7z()
    if seven_zip is not None:
        # the primary extractor may have left partial files; start clean
        shutil.rmtree(dest, ignore_errors=True)
        dest.mkdir(parents=True, exist_ok=True)
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
            _reject_traversal(dest, zf.namelist())
            zf.extractall(dest)
    except zipfile.BadZipFile as exc:
        raise CorruptArchive(str(exc)) from exc
    except NotImplementedError as exc:
        raise UnsupportedArchive("zip") from exc


def _un7z(path: Path, dest: Path) -> None:
    try:
        import lzma
        import py7zr
        from py7zr import exceptions as p7exc
    except ImportError as exc:
        raise UnsupportedArchive("7z") from exc
    try:
        with py7zr.SevenZipFile(path, mode="r") as zf:
            _reject_traversal(dest, zf.getnames())
            zf.extractall(path=dest)
    except ArchiveError:
        raise  # our own CorruptArchive/UnsupportedArchive (e.g. traversal) pass through
    except p7exc.UnsupportedCompressionMethodError as exc:
        raise UnsupportedArchive("7z") from exc  # let external 7-Zip try exotic methods
    except (p7exc.ArchiveError, p7exc.AbsolutePathError, p7exc.PasswordRequired,
            lzma.LZMAError, OSError, EOFError) as exc:
        raise CorruptArchive(str(exc)) from exc
    except Exception as exc:
        raise ArchiveError(str(exc)) from exc  # unexpected: don't mislabel as corrupt


def _unrar(path: Path, dest: Path) -> None:
    try:
        import rarfile
    except ImportError as exc:
        raise UnsupportedArchive("rar") from exc
    try:
        with rarfile.RarFile(path) as rf:
            _reject_traversal(dest, rf.namelist())
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


def _parse_7z_listing(text: str) -> list[str]:
    # entry names from `7z l -slt`: the archive header block comes first,
    # then a line of dashes, then one "Path = ..." per entry
    names: list[str] = []
    in_entries = False
    for line in text.splitlines():
        stripped = line.strip()
        if not in_entries:
            if len(stripped) >= 5 and set(stripped) == {"-"}:
                in_entries = True
            continue
        if stripped.startswith("Path = "):
            names.append(stripped[len("Path = "):])
    return names


def _run_7z(exe: str, args: list[str], flags: int):
    try:
        return subprocess.run(
            [exe, *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=flags,
        )
    except OSError as exc:
        raise ArchiveError(str(exc)) from exc


def _un_7zip(exe: str, path: Path, dest: Path) -> None:
    flags = 0
    if os.name == "nt":
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    listing = _run_7z(exe, ["l", "-slt", str(path)], flags)
    if listing.returncode != 0:
        detail = (listing.stderr or listing.stdout or b"").decode("utf-8", "ignore").strip()
        raise CorruptArchive(detail or f"7-Zip exited with {listing.returncode}")
    _reject_traversal(dest, _parse_7z_listing(listing.stdout.decode("utf-8", "ignore")))

    proc = _run_7z(exe, ["x", str(path), f"-o{dest}", "-y"], flags)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or b"").decode("utf-8", "ignore").strip()
        raise CorruptArchive(detail or f"7-Zip exited with {proc.returncode}")
