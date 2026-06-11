from __future__ import annotations

"""Pure-Python helpers for the "Dateien-Umbenenner" (vehicle replace renamer) tab.

A GTA-V replace vehicle ships a set of model files named after the game vehicle
(FBI.ytd, FBI.yft, FBI_hi.yft, FBI+hi.ytd, …). To install the set as a replacement
for a *different* game vehicle, every file must be renamed from the source model
name to the target model name while keeping its high-detail suffix and extension.
These helpers detect the common base name and plan the renames; they are kept
free of Qt so the logic is unit-testable (backend.py wraps them in Slots).
"""

import re
from pathlib import Path

# high-detail suffixes preserved during renaming (lowercase; extend to support
# further variants). Matched case-insensitively at the end of the file stem.
HI_SUFFIXES: tuple[str, ...] = ("_hi", "+hi")

# extensions that belong to a vehicle model file set (lowercase, with dot)
MODEL_EXTS: tuple[str, ...] = (".yft", ".ytd")

# everything the renamer treats as part of a vehicle set: model files plus the
# XML configs (e.g. ELS-VCF) that ship alongside and share the vehicle's name
RENAME_EXTS: tuple[str, ...] = MODEL_EXTS + (".xml",)

# GTA model names: lowercase letters/digits plus the few separators that appear
# in file names. Everything else is stripped so a preset can never produce an
# invalid or path-escaping file name.
_MODEL_RE = re.compile(r"[^a-z0-9_+\-]")

# default target presets seeded when the stored list is empty (display names are
# German on purpose — the app is German-first and presets are editable user data)
DEFAULT_PRESETS: tuple[tuple[str, str], ...] = (
    ("Polizei", "police"),
    ("Polizei 2", "police2"),
    ("Polizei 3", "police3"),
    ("Polizei 4", "police4"),
    ("FBI", "fbi"),
    ("FBI 2", "fbi2"),
    ("Ambulanz", "ambulance"),
    ("Polw", "policeold1"),      # uncertain mapping — plausible placeholder, editable
    ("Police T", "policet"),
    ("Police B", "policeb"),
    ("Sheriff", "sheriff"),
    ("Sheriff 2", "sheriff2"),
    ("Ranger", "pranger"),
)


def sanitize_model(name: str) -> str:
    """normalize a target model name: lowercase, no spaces/invalid characters."""
    return _MODEL_RE.sub("", (name or "").strip().lower())


def split_stem(stem: str) -> tuple[str, str]:
    """split a file stem into (base, hi-suffix). The suffix is "" or the canonical
    lowercase form from HI_SUFFIXES; matching is case-insensitive."""
    low = stem.lower()
    for suf in HI_SUFFIXES:
        if low.endswith(suf) and len(low) > len(suf):
            return stem[: -len(suf)], suf
    return stem, ""


def is_model_file(path: Path) -> bool:
    return path.suffix.lower() in MODEL_EXTS


def is_renameable(path: Path) -> bool:
    return path.suffix.lower() in RENAME_EXTS


def collect_files(paths: list[Path]) -> list[Path]:
    """flatten dropped paths: directories are expanded recursively, duplicates
    removed (case-insensitive), original order kept."""
    files: list[Path] = []
    for p in paths:
        try:
            if p.is_dir():
                files.extend(sorted(f for f in p.rglob("*") if f.is_file()))
            elif p.is_file():
                files.append(p)
        except OSError:
            continue
    seen: set[str] = set()
    out: list[Path] = []
    for f in files:
        key = str(f).lower()
        if key not in seen:
            seen.add(key)
            out.append(f)
    return out


def group_by_base(files: list[Path]) -> dict[str, list[Path]]:
    """group renameable files (models + XML) by their lowercase base name (stem
    minus hi-suffix). Other files are ignored."""
    groups: dict[str, list[Path]] = {}
    for f in files:
        if not is_renameable(f):
            continue
        base, _ = split_stem(f.stem)
        groups.setdefault(base.lower(), []).append(f)
    return groups


def detect_base(files: list[Path]) -> str:
    """the most common base candidate over all model files ("" if none).
    Ties resolve alphabetically so the result is deterministic."""
    groups = group_by_base(files)
    if not groups:
        return ""
    return sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0]))[0][0]


def routes_to_els(path: Path, xml_to_els: bool, els_available: bool,
                  is_els_xml=None) -> bool:
    """Should this renamed file be copied into the ELS folder instead of the
    model destination? Only XML files ever route to ELS, and only while the
    setting is on and an ELS folder is actually available. `is_els_xml(path)`
    optionally narrows routing to files whose content looks like an ELS-VCF
    (other XMLs then stay with the model files)."""
    if not xml_to_els or not els_available:
        return False
    if path.suffix.lower() != ".xml":
        return False
    return True if is_els_xml is None else bool(is_els_xml(path))


def plan_renames(files: list[Path], base: str, target_model: str) -> list[tuple[Path, str]]:
    """(source, new_file_name) for every renameable file whose base matches `base`.
    New name = target model + preserved hi-suffix + original extension, all
    lowercase (GTA expects lowercase model file names)."""
    target = sanitize_model(target_model)
    base = (base or "").lower()
    out: list[tuple[Path, str]] = []
    if not base:
        return out
    for f in files:
        if not is_renameable(f):
            continue
        b, suf = split_stem(f.stem)
        if b.lower() != base:
            continue
        out.append((f, f"{target}{suf}{f.suffix.lower()}"))
    return out
