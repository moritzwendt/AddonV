; AddonV installer — Inno Setup script
;
; Build flow:
;   1. PyInstaller builds dist/AddonV/  (onedir, windowed)
;   2. ISCC compiles this script and produces installer/output/AddonV-Setup-<ver>.exe
;
; Version is passed in by the build script / CI:
;     ISCC.exe /DMyAppVersion=1.0.0 installer.iss

#ifndef MyAppVersion
  #define MyAppVersion "0.0.0-dev"
#endif

#define MyAppName        "AddonV"
#define MyAppPublisher   "AddonV Contributors"
#define MyAppURL         "https://github.com/"
#define MyAppExeName     "AddonV.exe"

[Setup]
AppId={{6E9C0E0B-3A40-4B27-9F1F-AD2C92B7A6F0}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=output
OutputBaseFilename=AddonV-Setup-{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=AddonV.ico
ShowLanguageDialog=yes
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl";              LicenseFile: "eula_en.txt"
Name: "german";  MessagesFile: "compiler:Languages\German.isl";     LicenseFile: "eula_de.txt"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl";    LicenseFile: "eula_ru.txt"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl";    LicenseFile: "eula_es.txt"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; PyInstaller output is dist/AddonV/ (onedir). recursesubdirs picks up the whole tree.
Source: "..\dist\{#MyAppName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}";                            Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}";      Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}";                      Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
