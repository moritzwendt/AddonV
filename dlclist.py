from __future__ import annotations

import re
from pathlib import Path

from i18n import T


_ITEM_RE = re.compile(r"<Item>dlcpacks:/([^/<]+)/</Item>")
_PATHS_CLOSE_RE = re.compile(r"(\s*)</Paths>")
_EXISTING_ITEM_INDENT_RE = re.compile(r"^([ \t]+)<Item>dlcpacks:/", re.MULTILINE)
_DISABLED_RE = re.compile(r"<!--\s*<Item>dlcpacks:/([^/<]+)/</Item>\s*-->")
_ANY_ITEM_RE = re.compile(
    r"(?:<!--\s*)?<Item>dlcpacks:/([^/<]+)/</Item>(?:\s*-->)?"
)


def list_entries(xml_text: str) -> list[str]:
    return _ITEM_RE.findall(xml_text)


def list_active_entries(xml_text: str) -> list[str]:
    return _ITEM_RE.findall(_DISABLED_RE.sub("", xml_text))


def list_disabled_entries(xml_text: str) -> list[str]:
    return _DISABLED_RE.findall(xml_text)


def list_ordered_entries(xml_text: str) -> list[str]:
    return [m.group(1) for m in _ANY_ITEM_RE.finditer(xml_text)]


def find_duplicate_entries(xml_text: str) -> list[str]:
    seen: set[str] = set()
    dupes: set[str] = set()
    for name in list_ordered_entries(xml_text):
        if name in seen:
            dupes.add(name)
        seen.add(name)
    return sorted(dupes)


def set_order(xml_text: str, ordered_names: list[str]) -> str:
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
    return (
        xml_text[: ma.start()]
        + mb.group(0)
        + xml_text[ma.end() : mb.start()]
        + ma.group(0)
        + xml_text[mb.end() :]
    )


def add_dlc_entry(xml_text: str, dlc_name: str) -> str:
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
        rf"[ \t]*(?:<!--\s*)?<Item>dlcpacks:/{re.escape(dlc_name)}/</Item>(?:\s*-->)?\r?\n?",
        re.MULTILINE,
    )
    return pattern.sub("", xml_text, count=1)


def disable_dlc_entry(xml_text: str, dlc_name: str) -> str:
    if dlc_name in list_disabled_entries(xml_text):
        return xml_text
    pattern = re.compile(rf"(<Item>dlcpacks:/{re.escape(dlc_name)}/</Item>)")
    return pattern.sub(r"<!-- \1 -->", xml_text, count=1)


def enable_dlc_entry(xml_text: str, dlc_name: str) -> str:
    pattern = re.compile(
        rf"<!--\s*(<Item>dlcpacks:/{re.escape(dlc_name)}/</Item>)\s*-->"
    )
    return pattern.sub(r"\1", xml_text, count=1)


_PROFILE_START = "ADDONV_START:"
_PROFILE_END = "ADDONV_END:"


def _item_indent(xml_text: str, paths_match) -> str:
    existing = _EXISTING_ITEM_INDENT_RE.search(xml_text)
    if existing:
        return existing.group(1)
    paths_indent = paths_match.group(1).lstrip("\n\r")
    return (paths_indent * 2) if paths_indent else "\t\t"


def comment_profile_block(xml_text: str, profile_id: str, profile_name: str,
                          dlc_names: list[str]) -> str:
    wanted = set(dlc_names)
    present = [n for n in list_ordered_entries(xml_text) if n in wanted]
    seen: set[str] = set()
    present = [n for n in present if not (n in seen or seen.add(n))]
    if not present:
        return xml_text
    for n in present:
        xml_text = remove_dlc_entry(xml_text, n)
    match = _PATHS_CLOSE_RE.search(xml_text)
    if not match:
        raise ValueError(T("dlclist_paths_close_missing"))
    indent = _item_indent(xml_text, match)
    lines = [f"{indent}<!-- {_PROFILE_START}{profile_id} | Profil: {profile_name} -->"]
    for n in present:
        lines.append(f"{indent}<!-- <Item>dlcpacks:/{n}/</Item> -->")
    lines.append(f"{indent}<!-- {_PROFILE_END}{profile_id} | Profil: {profile_name} -->")
    block = "\n" + "\n".join(lines)
    return xml_text[: match.start()] + block + xml_text[match.start():]


def uncomment_profile_block(xml_text: str, profile_id: str) -> str:
    pat = re.compile(
        r"[ \t]*<!--\s*" + re.escape(_PROFILE_START + str(profile_id)) + r"\b.*?-->[ \t]*\r?\n?"
        r"(.*?)"
        r"[ \t]*<!--\s*" + re.escape(_PROFILE_END + str(profile_id)) + r"\b.*?-->[ \t]*\r?\n?",
        re.DOTALL,
    )
    m = pat.search(xml_text)
    if not m:
        return xml_text
    names = _ANY_ITEM_RE.findall(m.group(1))
    xml_text = xml_text[: m.start()] + xml_text[m.end():]
    for n in names:
        xml_text = add_dlc_entry(xml_text, n)
    return xml_text


def comment_profile_in_file(xml_path: Path, profile_id: str, profile_name: str,
                            dlc_names: list[str]) -> bool:
    return _edit_file(
        xml_path,
        lambda text: comment_profile_block(text, profile_id, profile_name, dlc_names),
    )


def uncomment_profile_in_file(xml_path: Path, profile_id: str) -> bool:
    return _edit_file(xml_path, lambda text: uncomment_profile_block(text, profile_id))


def update_file(xml_path: Path, dlc_name: str) -> bool:
    return _edit_file(xml_path, lambda text: add_dlc_entry(text, dlc_name))


def remove_from_file(xml_path: Path, dlc_name: str) -> bool:
    return _edit_file(xml_path, lambda text: remove_dlc_entry(text, dlc_name))


def disable_in_file(xml_path: Path, dlc_name: str) -> bool:
    return _edit_file(xml_path, lambda text: disable_dlc_entry(text, dlc_name))


def enable_in_file(xml_path: Path, dlc_name: str) -> bool:
    return _edit_file(xml_path, lambda text: enable_dlc_entry(text, dlc_name))


def move_in_file(xml_path: Path, dlc_name: str, delta: int) -> bool:
    return _edit_file(xml_path, lambda text: move_entry(text, dlc_name, delta))


def set_order_in_file(xml_path: Path, ordered_names: list[str]) -> bool:
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
