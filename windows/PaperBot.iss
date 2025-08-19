#define MyAppName "PaperBot"
#define MyAppVersion "1.5.0"
#define MyAppPublisher "Syklic"
#define MyAppExeName "PaperBot.exe"

[Setup]
AppId={{5B27C6C8-90B0-4A8B-8F9D-92E74D2A7D21}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=windows
OutputBaseFilename=PaperBot-Setup
SetupIconFile=icons\app-icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "dist\PaperBot\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs
Source: "icons\app-icon.ico"; DestDir: "{app}\icons"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent


