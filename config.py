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
    # auto-collapse the sidebar: stays collapsed, expands only while hovered
    sidebar_auto_collapse: bool = False
    # A2 redesign — DLC-Packs sort state (sortKey: name|created|added, dir: asc|desc)
    pack_sort_key: str = "added"
    pack_sort_dir: str = "desc"
    # behaviour toggles (settings → Verhalten)
    auto_maintain_dlclist: bool = True
    detect_els: bool = True
    # file renamer: copy renamed ELS-VCF XMLs into the ELS folder instead of the
    # chosen destination folder (model files always go to the destination)
    rename_xml_to_els: bool = True
    # name -> unix timestamp of when the pack was imported into AddonV
    import_dates: dict = field(default_factory=dict)
    # saved mod loadouts ("Profile"): each is
    #   {"id": str, "name": str, "dlc": [pack names], "els": [vcf file names]}
    # dlc/els list which packs / ELS files should be ACTIVE while the profile runs.
    profiles: list = field(default_factory=list)
    # id of the currently applied profile ("" = none; only one is ever active)
    active_profile: str = ""
    # custom drop zones on the Install page (max 4, laid out on a 2x2 grid). Each:
    #   {"id": str, "name": str, "auto": bool, "rel": str, "color": str,
    #    "col": 0|1, "row": 0|1, "w": 1|2, "h": 1|2}
    # "auto" zones run the smart DLC/ELS detector; otherwise files are copied verbatim
    # into <gta_path>/<rel> (rel is always kept inside the GTA root). An empty list is
    # seeded with a single full-size auto zone by the backend (= classic behaviour).
    drop_zones: list = field(default_factory=list)
    # file-renamer tab: target vehicle presets, each {"id": str, "name": str, "model": str}.
    # An empty list is seeded with the defaults by the backend (analogous to drop_zones).
    rename_presets: list = field(default_factory=list)
    # last destination folder used by the file renamer
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
