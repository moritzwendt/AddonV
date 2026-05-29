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


def list_entries(xml_text: str) -> list[str]:
    return _ITEM_RE.findall(xml_text)


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
    pattern = re.compile(
        rf"[ \t]*<Item>dlcpacks:/{re.escape(dlc_name)}/</Item>\r?\n?",
        re.MULTILINE,
    )
    return pattern.sub("", xml_text, count=1)


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


def _edit_file(xml_path: Path, transform) -> bool:
    text = xml_path.read_text(encoding="utf-8")
    new_text = transform(text)
    if new_text == text:
        return False
    backup = xml_path.with_suffix(xml_path.suffix + ".bak")
    if not backup.exists():
        backup.write_text(new_text, encoding="utf-8")
    xml_path.write_text(new_text, encoding="utf-8")
    return True
