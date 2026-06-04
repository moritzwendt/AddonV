"""Read and modify dlclist.xml content.

We use a regex-based approach instead of a real XML parser to preserve the
original file's formatting and avoid normalising indentation, which OpenIV
re-imports more cleanly.
"""
from __future__ import annotations

import re
from pathlib import Path

from i18n import T


_ITEM_RE = re.compile(r"<Item>dlcpacks:/([^/<]+)/</Item>")
_PATHS_CLOSE_RE = re.compile(r"(\s*)</Paths>")
_EXISTING_ITEM_INDENT_RE = re.compile(r"^([ \t]+)<Item>dlcpacks:/", re.MULTILINE)
# A disabled entry is the normal <Item> wrapped in an XML comment, so OpenIV/the
# game ignores it while the user can still see the pack is only switched off (not
# missing). We allow optional inner whitespace so hand-edited comments still match.
_DISABLED_RE = re.compile(r"<!--\s*<Item>dlcpacks:/([^/<]+)/</Item>\s*-->")
# Matches a single pack line in load order, active or disabled (comment and all),
# without its leading indentation — used to read and reorder the load order.
_ANY_ITEM_RE = re.compile(
    r"(?:<!--\s*)?<Item>dlcpacks:/([^/<]+)/</Item>(?:\s*-->)?"
)


def list_entries(xml_text: str) -> list[str]:
    """All registered packs, whether active or disabled (commented out)."""
    return _ITEM_RE.findall(xml_text)


def list_active_entries(xml_text: str) -> list[str]:
    """Packs that are actually loaded (not inside a disabling comment)."""
    return _ITEM_RE.findall(_DISABLED_RE.sub("", xml_text))


def list_disabled_entries(xml_text: str) -> list[str]:
    """Packs whose <Item> is commented out."""
    return _DISABLED_RE.findall(xml_text)


def list_ordered_entries(xml_text: str) -> list[str]:
    """All packs in their load order as written in the file (active or disabled)."""
    return [m.group(1) for m in _ANY_ITEM_RE.finditer(xml_text)]


def find_duplicate_entries(xml_text: str) -> list[str]:
    """Pack names that appear more than once in the list (a real load conflict)."""
    seen: set[str] = set()
    dupes: set[str] = set()
    for name in list_ordered_entries(xml_text):
        if name in seen:
            dupes.add(name)
        seen.add(name)
    return sorted(dupes)


def set_order(xml_text: str, ordered_names: list[str]) -> str:
    """Rewrite the load order so the entries follow `ordered_names`.

    Each `<Item>` line keeps its exact text (active/disabled state included) and
    the file's indentation — only the order of the lines changes. Names missing
    from `ordered_names` keep their original relative position at the end. Returns
    unchanged text if the list has duplicate names (order would be ambiguous).
    """
    matches = list(_ANY_ITEM_RE.finditer(xml_text))
    names = [m.group(1) for m in matches]
    if len(set(names)) != len(names):
        return xml_text
    cores = {m.group(1): m.group(0) for m in matches}
    seq = [n for n in ordered_names if n in cores]
    seq += [n for n in names if n not in seq]
    if seq == names:
        return xml_text
    out: list[str] = []
    last = 0
    for m, name in zip(matches, seq):
        out.append(xml_text[last : m.start()])
        out.append(cores[name])
        last = m.end()
    out.append(xml_text[last:])
    return "".join(out)


def move_entry(xml_text: str, dlc_name: str, delta: int) -> str:
    """Move a pack up (delta<0) or down (delta>0) in the load order.

    Swaps the whole `<Item>` line (keeping each item's active/disabled state and
    the file's existing indentation) with its neighbour. Returns unchanged text
    if the move would run past either end.
    """
    matches = list(_ANY_ITEM_RE.finditer(xml_text))
    names = [m.group(1) for m in matches]
    if dlc_name not in names:
        return xml_text
    i = names.index(dlc_name)
    j = i + delta
    if j < 0 or j >= len(matches):
        return xml_text
    a, b = sorted((i, j))
    ma, mb = matches[a], matches[b]
    # Swap only the item cores; the surrounding whitespace/indentation stays put.
    return (
        xml_text[: ma.start()]
        + mb.group(0)
        + xml_text[ma.end() : mb.start()]
        + ma.group(0)
        + xml_text[mb.end() :]
    )


def add_dlc_entry(xml_text: str, dlc_name: str) -> str:
    """Insert `<Item>dlcpacks:/<dlc_name>/</Item>` before `</Paths>`.

    Returns the (possibly unchanged) XML text.
    """
    if dlc_name in list_entries(xml_text):
        return xml_text
    match = _PATHS_CLOSE_RE.search(xml_text)
    if not match:
        raise ValueError(T("dlclist_paths_close_missing"))

    existing = _EXISTING_ITEM_INDENT_RE.search(xml_text)
    if existing:
        item_indent = existing.group(1)
    else:
        paths_indent = match.group(1).lstrip("\n\r")
        item_indent = (paths_indent * 2) if paths_indent else "\t\t"

    new_item = f"\n{item_indent}<Item>dlcpacks:/{dlc_name}/</Item>"
    return xml_text[: match.start()] + new_item + xml_text[match.start():]


def remove_dlc_entry(xml_text: str, dlc_name: str) -> str:
    # Match the entry whether it's active or wrapped in a disabling comment, so
    # removing a pack cleans up either form (and leaves no dangling <!-- -->).
    pattern = re.compile(
        rf"[ \t]*(?:<!--\s*)?<Item>dlcpacks:/{re.escape(dlc_name)}/</Item>(?:\s*-->)?\r?\n?",
        re.MULTILINE,
    )
    return pattern.sub("", xml_text, count=1)


def disable_dlc_entry(xml_text: str, dlc_name: str) -> str:
    """Comment out an active entry; a no-op if it's already disabled or absent."""
    if dlc_name in list_disabled_entries(xml_text):
        return xml_text
    pattern = re.compile(rf"(<Item>dlcpacks:/{re.escape(dlc_name)}/</Item>)")
    return pattern.sub(r"<!-- \1 -->", xml_text, count=1)


def enable_dlc_entry(xml_text: str, dlc_name: str) -> str:
    """Uncomment a disabled entry; a no-op if it's already active or absent."""
    pattern = re.compile(
        rf"<!--\s*(<Item>dlcpacks:/{re.escape(dlc_name)}/</Item>)\s*-->"
    )
    return pattern.sub(r"\1", xml_text, count=1)


def update_file(xml_path: Path, dlc_name: str) -> bool:
    """Add an entry to the file; create a single .bak before first edit.

    Returns True if the file was actually modified.
    """
    return _edit_file(xml_path, lambda text: add_dlc_entry(text, dlc_name))


def remove_from_file(xml_path: Path, dlc_name: str) -> bool:
    """Remove an entry from the file; create a single .bak before first edit.

    Returns True if the file was actually modified.
    """
    return _edit_file(xml_path, lambda text: remove_dlc_entry(text, dlc_name))


def disable_in_file(xml_path: Path, dlc_name: str) -> bool:
    """Comment out an entry; create a single .bak before first edit.

    Returns True if the file was actually modified.
    """
    return _edit_file(xml_path, lambda text: disable_dlc_entry(text, dlc_name))


def enable_in_file(xml_path: Path, dlc_name: str) -> bool:
    """Uncomment an entry; create a single .bak before first edit.

    Returns True if the file was actually modified.
    """
    return _edit_file(xml_path, lambda text: enable_dlc_entry(text, dlc_name))


def move_in_file(xml_path: Path, dlc_name: str, delta: int) -> bool:
    """Reorder an entry in the file; create a single .bak before first edit.

    Returns True if the file was actually modified.
    """
    return _edit_file(xml_path, lambda text: move_entry(text, dlc_name, delta))


def set_order_in_file(xml_path: Path, ordered_names: list[str]) -> bool:
    """Apply a full load order to the file; create a single .bak before first edit.

    Returns True if the file was actually modified.
    """
    return _edit_file(xml_path, lambda text: set_order(text, ordered_names))


def _edit_file(xml_path: Path, transform) -> bool:
    text = xml_path.read_text(encoding="utf-8")
    new_text = transform(text)
    if new_text == text:
        return False
    backup = xml_path.with_suffix(xml_path.suffix + ".bak")
    if not backup.exists():
        backup.write_text(text, encoding="utf-8")
    xml_path.write_text(new_text, encoding="utf-8")
    return True
