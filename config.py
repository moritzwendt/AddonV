from __future__ import annotations

import json
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

    @classmethod
    def load(cls) -> "Config":
        if not CONFIG_FILE.exists():
            return cls()
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except Exception:
            return cls()

    def save(self) -> None:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
