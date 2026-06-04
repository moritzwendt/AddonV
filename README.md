# AddonV

A small open-source GUI tool to install GTA V single-player mods
(Add-On DLCs and ELS-VCF vehicle configs) by drag-and-drop.

## Install (end users)

1. Go to the [Releases page](../../releases) and download the latest
   `AddonV-Setup-<version>.exe`.
2. Run it. Choose your language, accept the license/disclaimer, and
   follow the installer wizard.
3. Launch AddonV from the Start Menu. Drag a DLC folder or an
   `els.xml` onto the matching drop zone.

> **Note:** AddonV is unsigned. Windows SmartScreen may warn on first
> launch. Click "More info" → "Run anyway".

## Features

- Auto-detects your GTA V installation
- Safe-by-default: installs into the OpenIV `mods/` subfolder
- Optional direct-install mode (with explicit warning)
- DLC drop zone — copies into `dlcpacks/` and patches `dlclist.xml`
- ELS drop zone — copies ELS-VCF files into `ELS/pack_default/`
- Archive drop — drop a `.zip`/`.oiv`/`.7z`/`.rar`; it's extracted to a temp
  folder, scanned for DLC packs and ELS files, installed, then cleaned up. The
  real format is detected from the file's contents (a mislabelled archive still
  opens), and corrupt files are reported as such. ZIP/OIV and 7z work out of the
  box; installing [7-Zip](https://7-zip.org) enables every format including RAR.
- Mod manager — enable/disable packs (commented out in `dlclist.xml`),
  reorder the load order by drag-and-drop, repair the list, and spot duplicates
- Auto-update — checks GitHub Releases on startup and offers to download and
  install a newer version; can be re-checked from Settings or turned off
- Settings — language, terminal-history persistence, and update preference
- Persistent config in `%USERPROFILE%\.addonv\config.json`

## Build it yourself

### Prerequisites

- Python 3.10+
- [Inno Setup 6](https://jrsoftware.org/isdl.php) (for the installer)

### Steps

```powershell
git clone <repo-url> AddonV
cd AddonV
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt pyinstaller

# Build dev installer
.\build.ps1

# Build tagged release locally
.\build.ps1 -Version 1.0.0
```

Output: `installer/output/AddonV-Setup-<version>.exe`.

### CI builds

Pushing a tag like `v1.0.0` triggers `.github/workflows/release.yml`,
which builds the installer on a Windows runner and attaches it to a
new GitHub Release.

## Disclaimer

This tool modifies files in your GTA V installation. Modding may
violate Rockstar's EULA and **must not** be used with GTA Online.
Use at your own risk. The full license/disclaimer is shown during
installation and is also in [`installer/eula_en.txt`](installer/eula_en.txt).

## License

[MIT](LICENSE).
