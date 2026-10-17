from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path


CONFIG_FILE = Path.home() / ".addonv" / "config.json"


@dataclass
class Config:
    gta_path: str = ""
    use_mods_folder: bool = True
    dlclist_xml_path: str = ""
    language: str = ""
    manage_sort: str = "name"
    save_terminal_history: bool = True
    terminal_history: list = field(default_factory=list)
    auto_check_updates: bool = True
    accent: str = "#50a064"
    sidebar_collapsed: bool = False
    sidebar_auto_collapse: bool = False
    pack_sort_key: str = "added"
    pack_sort_dir: str = "desc"
    auto_maintain_dlclist: bool = True
    detect_els: bool = True
    rename_xml_to_els: bool = True
    import_dates: dict = field(default_factory=dict)
    profiles: list = field(default_factory=list)
    active_profile: str = ""
    drop_zones: list = field(default_factory=list)
    rename_presets: list = field(default_factory=list)
    rename_last_dest: str = ""

    # not a dataclass field (no annotation), so it is never written to disk:
    # where an unreadable config.json was moved to, set by load()
    broken_copy = ""

    @classmethod
    def load(cls) -> "Config":
        if not CONFIG_FILE.exists():
            return cls()
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except OSError:
            return cls()  # locked / unreadable right now: leave the file alone
        except (ValueError, AttributeError, TypeError):
            # not valid JSON (or not an object): keep the file instead of letting
            # the next save() silently overwrite everything the user had
            cfg = cls()
            cfg.broken_copy = _set_aside(CONFIG_FILE)
            return cfg

    def save(self) -> None:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        # write the whole file next to the real one, then swap it in, so a crash
        # or power loss mid-write can never leave a half-written config.json
        tmp = CONFIG_FILE.with_name(CONFIG_FILE.name + ".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(json.dumps(asdict(self), indent=2))
                f.flush()
                os.fsync(f.fileno())
            _replace(tmp, CONFIG_FILE)
        except BaseException:
            try:
                tmp.unlink()
            except OSError:
                pass
            raise


def _replace(src: Path, dst: Path) -> None:
    # Windows refuses the swap for a moment if a virus scanner or sync tool has
    # the file open; a short retry covers that
    for attempt in range(5):
        try:
            os.replace(src, dst)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.05)


def _set_aside(path: Path) -> str:
    dest = path.with_name(path.name + ".broken")
    try:
        os.replace(path, dest)
    except OSError:
        return ""
    return str(dest)
