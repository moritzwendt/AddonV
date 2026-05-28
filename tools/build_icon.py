"""Convert logo.png into a multi-resolution Windows .ico for the build.

Called by build.ps1 and by the GitHub Actions workflow before PyInstaller
runs. Idempotent: re-runs only when the source is newer than the output.

Pillow is a build-time-only dependency — not part of requirements.txt.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.stderr.write(
        "Pillow not installed. Run:\n  pip install pillow\n"
    )
    sys.exit(1)


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "logo.png"
DST = ROOT / "installer" / "AddonV.ico"

# Standard Windows icon resolutions. 256 enables high-DPI Explorer thumbnails.
SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def main() -> int:
    if not SRC.exists():
        sys.stderr.write(f"Source icon missing: {SRC}\n")
        return 1
    if DST.exists() and DST.stat().st_mtime >= SRC.stat().st_mtime:
        print(f"[icon] up to date: {DST.relative_to(ROOT)}")
        return 0

    DST.parent.mkdir(parents=True, exist_ok=True)
    img = Image.open(SRC).convert("RGBA")

    # Render into a memory buffer first, then write bytes ourselves.
    # Pillow's direct path-based ICO save uses open(path, "w+b") which fails
    # on some Windows setups (Controlled Folder Access, Defender heuristics).
    buf = io.BytesIO()
    img.save(buf, format="ICO", sizes=SIZES)
    DST.write_bytes(buf.getvalue())

    print(f"[icon] wrote {DST.relative_to(ROOT)} ({DST.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
