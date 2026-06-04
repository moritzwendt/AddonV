from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from version import __version__ as CURRENT_VERSION


REPO = "moritzwendt/AddonV"
API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"
_UA = "AddonV-Updater"

ProgressFn = Callable[[int, int], None]


@dataclass
class UpdateInfo:
    version: str
    asset_url: str
    page_url: str
    notes: str


def _parse(v: str) -> tuple[int, ...]:
    # turn a tag like "v1.2.3" into (1, 2, 3) for comparison
    return tuple(int(x) for x in re.findall(r"\d+", v)) or (0,)


def is_newer(latest: str, current: Optional[str] = None) -> bool:
    return _parse(latest) > _parse(current or CURRENT_VERSION)


def fetch_latest(timeout: int = 10) -> Optional[UpdateInfo]:
    req = urllib.request.Request(
        API_URL,
        headers={"User-Agent": _UA, "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.load(resp)
    tag = data.get("tag_name") or ""
    if not tag:
        return None
    # prefer the Windows installer asset
    asset_url = ""
    for asset in data.get("assets") or []:
        name = (asset.get("name") or "").lower()
        if name.endswith(".exe"):
            asset_url = asset.get("browser_download_url") or ""
            break
    return UpdateInfo(
        version=tag,
        asset_url=asset_url,
        page_url=data.get("html_url") or "",
        notes=data.get("body") or "",
    )


def check_for_update(timeout: int = 10) -> Optional[UpdateInfo]:
    # returns the release only if it is newer than what is running
    info = fetch_latest(timeout=timeout)
    if info and is_newer(info.version):
        return info
    return None


def download_installer(info: UpdateInfo, progress: Optional[ProgressFn] = None) -> Path:
    dest_dir = Path(tempfile.mkdtemp(prefix="addonv_upd_"))
    dest = dest_dir / (info.asset_url.split("/")[-1] or "AddonV-Setup.exe")
    req = urllib.request.Request(info.asset_url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=30) as resp, open(dest, "wb") as f:
        total = int(resp.headers.get("Content-Length") or 0)
        done = 0
        while True:
            chunk = resp.read(64 * 1024)
            if not chunk:
                break
            f.write(chunk)
            done += len(chunk)
            if progress is not None:
                progress(done, total)
    return dest


def run_installer(path: Path) -> None:
    # launch the downloaded installer; the caller then quits so files can swap
    if os.name == "nt":
        os.startfile(str(path))  # type: ignore[attr-defined]
    else:
        subprocess.Popen([str(path)])
