"""Unit tests for archive.py (extracting dropped zip / 7z / rar files safely).

Run with:  py -3 tests\\test_archive.py   — or —  py -3 -m pytest tests
"""
from __future__ import annotations

import sys
import zipfile
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import archive
from _runner import run


@contextmanager
def no_external_7zip():
    # a 7-Zip on this machine would change which code path handles bad archives
    real = archive._find_7z
    archive._find_7z = lambda: None
    try:
        yield
    finally:
        archive._find_7z = real


@contextmanager
def tracked_temp_dirs():
    """record every temp folder extract_to_temp creates, so tests can check cleanup"""
    created: list[Path] = []
    real = archive.tempfile.mkdtemp

    def tracking(*args, **kwargs):
        path = real(*args, **kwargs)
        created.append(Path(path))
        return path

    archive.tempfile.mkdtemp = tracking
    try:
        yield created
    finally:
        archive.tempfile.mkdtemp = real


def _make_zip(path: Path, entries: dict[str, str]) -> Path:
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)
    return path


def _cleanup(created):
    import shutil
    for d in created:
        shutil.rmtree(d, ignore_errors=True)


def test_is_archive(tmp: Path):
    z = _make_zip(tmp / "a.zip", {"x.txt": "x"})
    assert archive.is_archive(z)
    plain = tmp / "a.txt"
    plain.write_text("x")
    assert not archive.is_archive(plain)
    assert not archive.is_archive(tmp / "missing.zip")
    assert not archive.is_archive(tmp)  # a folder, even if named like one


def test_zip_extracts_into_a_folder_named_after_the_archive(tmp: Path):
    z = _make_zip(tmp / "mypack.zip", {"dlc.rpf": "data", "sub/readme.txt": "hi"})
    with tracked_temp_dirs() as created:
        dest = archive.extract_to_temp(z)
        try:
            assert dest.name == "mypack"
            assert (dest / "dlc.rpf").read_text() == "data"
            assert (dest / "sub" / "readme.txt").read_text() == "hi"
        finally:
            _cleanup(created)


def test_oiv_is_treated_as_a_zip(tmp: Path):
    z = _make_zip(tmp / "mod.oiv", {"content/a.txt": "x"})
    with tracked_temp_dirs() as created:
        dest = archive.extract_to_temp(z)
        try:
            assert (dest / "content" / "a.txt").exists()
        finally:
            _cleanup(created)


def test_mislabelled_archive_is_detected_by_content(tmp: Path):
    real_zip = _make_zip(tmp / "real.zip", {"a.txt": "x"})
    wrong_name = tmp / "actually_a_zip.rar"
    wrong_name.write_bytes(real_zip.read_bytes())
    with tracked_temp_dirs() as created:
        dest = archive.extract_to_temp(wrong_name)
        try:
            assert (dest / "a.txt").exists()
        finally:
            _cleanup(created)


def test_corrupt_archive_is_reported_and_leaves_no_temp_folder(tmp: Path):
    bad = tmp / "broken.zip"
    bad.write_bytes(b"PK\x03\x04 this is not really a zip file")
    with no_external_7zip(), tracked_temp_dirs() as created:
        try:
            archive.extract_to_temp(bad)
        except archive.CorruptArchive:
            pass
        else:
            raise AssertionError("expected CorruptArchive")
        assert created and not any(d.exists() for d in created)


def test_zip_slip_is_refused(tmp: Path):
    evil = _make_zip(tmp / "evil.zip", {"../escaped.txt": "gotcha", "ok.txt": "fine"})
    with no_external_7zip(), tracked_temp_dirs() as created:
        try:
            archive.extract_to_temp(evil)
        except archive.CorruptArchive:
            pass
        else:
            raise AssertionError("expected CorruptArchive")
        # nothing was written next to the temp folder, and the temp folder is gone
        assert all(not (d.parent / "escaped.txt").exists() for d in created)
        assert not any(d.exists() for d in created)


def test_unknown_format_without_7zip_is_unsupported(tmp: Path):
    rar = tmp / "thing.rar"
    rar.write_bytes(b"this is not a rar file and has no magic bytes")
    with no_external_7zip(), tracked_temp_dirs() as created:
        try:
            archive.extract_to_temp(rar)
        except archive.UnsupportedArchive:
            pass
        else:
            raise AssertionError("expected UnsupportedArchive")
        assert not any(d.exists() for d in created)


def test_7z_extracts_when_py7zr_is_available(tmp: Path):
    try:
        import py7zr
    except ImportError:
        print("      (skipped: py7zr not installed)")
        return
    src = tmp / "payload.txt"
    src.write_text("seven")
    packed = tmp / "pack.7z"
    with py7zr.SevenZipFile(packed, "w") as zf:
        zf.write(src, "payload.txt")
    with tracked_temp_dirs() as created:
        dest = archive.extract_to_temp(packed)
        try:
            assert (dest / "payload.txt").read_text() == "seven"
        finally:
            _cleanup(created)


def test_parse_7z_listing():
    listing = (
        "Listing archive: x.7z\n\n--\nPath = x.7z\nType = 7z\n\n----------\n"
        "Path = dlc.rpf\nSize = 4\n\nPath = sub/readme.txt\nSize = 2\n"
    )
    assert archive._parse_7z_listing(listing) == ["dlc.rpf", "sub/readme.txt"]


if __name__ == "__main__":
    raise SystemExit(run(globals()))
