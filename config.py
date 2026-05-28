"""Persistent user settings (JSON-backed)."""
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
    install_log: list = field(default_factory=list)

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
