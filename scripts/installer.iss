#define MyAppVersion "1.1.0-rc1"
[Setup]
AppId={{D64EE0C2-A5B2-438D-8EF4-66A01A32E783}
AppName=The Thrifty Pilot | Aircraft Maintenance Logbook
AppVersion={#MyAppVersion}
AppPublisher=The Thrifty Pilot
AppPublisherURL=https://www.thethriftypilot.com/
DefaultDirName={localappdata}\Programs\TheThriftyPilot\AircraftMaintenanceLogbook
DefaultGroupName=The Thrifty Pilot
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
OutputDir=..\dist\release
OutputBaseFilename=TheThriftyPilot-AircraftMaintenanceLogbook-Setup-{#MyAppVersion}
SetupIconFile=..\resources\app.ico
UninstallDisplayIcon={app}\AircraftMaintenanceLogbook.exe
LicenseFile=..\LICENSE
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no
VersionInfoVersion=1.1.0.1
[Tasks]
Name: desktopicon; Description: "Create a desktop shortcut"; Flags: unchecked
[Files]
Source: "..\dist\AircraftMaintenanceLogbook\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\Aircraft Maintenance Logbook"; Filename: "{app}\AircraftMaintenanceLogbook.exe"
Name: "{autodesktop}\Aircraft Maintenance Logbook"; Filename: "{app}\AircraftMaintenanceLogbook.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\AircraftMaintenanceLogbook.exe"; Description: "Open Aircraft Maintenance Logbook"; Flags: nowait postinstall skipifsilent
; No UninstallDelete section: user data is intentionally retained outside {app}.
