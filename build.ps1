# Local build script: produces installer/output/AddonV-Setup-<ver>.exe
#
# Usage:
#   .\build.ps1                 # builds dev version (0.0.0-dev)
#   .\build.ps1 -Version 1.0.0  # tagged build
#
# Requirements on the machine running this script:
#   - Python 3.10+ with PySide6 + pyinstaller installed
#   - Inno Setup 6 installed (ISCC.exe on PATH or at the default location)

param(
    [string]$Version = "0.0.0-dev"
)

$ErrorActionPreference = "Stop"

Write-Host "==> Cleaning previous build artifacts"
Remove-Item -Recurse -Force build, dist, installer\output -ErrorAction SilentlyContinue

Write-Host "==> Generating Windows .ico from logo.png"
python -m pip install --quiet --disable-pip-version-check pillow
if ($LASTEXITCODE -ne 0) { throw "pip install pillow failed" }
python tools\build_icon.py
if ($LASTEXITCODE -ne 0) { throw "icon generation failed" }

Write-Host "==> Building application with PyInstaller (version $Version)"
python -m PyInstaller --noconfirm AddonV.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

Write-Host "==> Locating Inno Setup compiler (ISCC.exe)"
$iscc = (Get-Command ISCC.exe -ErrorAction SilentlyContinue).Source
if (-not $iscc) {
    $candidates = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { $iscc = $c; break }
    }
}
if (-not $iscc) { throw "ISCC.exe not found. Install Inno Setup 6 from https://jrsoftware.org/isdl.php" }

Write-Host "==> Compiling installer with $iscc"
& $iscc "/DMyAppVersion=$Version" installer\installer.iss
if ($LASTEXITCODE -ne 0) { throw "Inno Setup compilation failed" }

Write-Host ""
Write-Host "==> Done. Installer:" -ForegroundColor Green
Get-ChildItem installer\output\*.exe | Select-Object FullName, Length | Format-Table -AutoSize
