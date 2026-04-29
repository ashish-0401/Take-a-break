; Inno Setup script for take-a-break.
; Build with:   "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" packaging\installer.iss
; Inno Setup is free: https://jrsoftware.org/isdl.php

#define AppName     "Take a Break"
#define AppId       "{{8E4F2C30-7A1E-4D0A-9F44-CA1234567890}"
#define AppVersion  "1.0.0"
#define AppPublisher "Your Name"
#define AppExeName  "take-a-break.exe"

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\dist-installer
OutputBaseFilename=take-a-break-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=..\assets\chubby-cat.png
UninstallDisplayName={#AppName}

[Files]
; Bundle everything PyInstaller produced.
Source: "..\dist\take-a-break\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{userprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{userstartup}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: autostart

[Tasks]
Name: "autostart"; Description: "Start automatically when I log in"; GroupDescription: "Startup:"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName} now"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "powershell.exe"; \
    Parameters: "-NoProfile -Command ""Stop-Process -Name take-a-break -Force -ErrorAction SilentlyContinue"""; \
    Flags: runhidden

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\take-a-break"

; ------------------------------------------------------------------
; Settings wizard page — writes %APPDATA%\take-a-break\config.json
; ------------------------------------------------------------------
[Code]
var
  SettingsPage: TInputQueryWizardPage;

procedure InitializeWizard;
begin
  SettingsPage := CreateInputQueryPage(
    wpSelectTasks,
    'Reminder Settings',
    'Customize your break reminders',
    'You can change these later by editing %APPDATA%\take-a-break\config.json'
  );
  SettingsPage.Add('Interval (minutes between breaks):', False);
  SettingsPage.Add('Work start hour (0-23):', False);
  SettingsPage.Add('Work end hour (0-23):', False);
  SettingsPage.Add('Title message:', False);
  SettingsPage.Add('Sub message:', False);

  // Defaults
  SettingsPage.Values[0] := '30';
  SettingsPage.Values[1] := '9';
  SettingsPage.Values[2] := '18';
  SettingsPage.Values[3] := 'I see you!';
  SettingsPage.Values[4] := 'Get up. Look out the window. Drink some water.';
end;

function WriteUserConfig(): Boolean;
var
  Dir, Path, S: string;
  Interval, StartH, EndH: Integer;
begin
  Result := True;
  Dir := ExpandConstant('{userappdata}\take-a-break');
  if not DirExists(Dir) then ForceDirectories(Dir);
  Path := Dir + '\config.json';

  Interval := StrToIntDef(SettingsPage.Values[0], 30);
  StartH   := StrToIntDef(SettingsPage.Values[1], 9);
  EndH     := StrToIntDef(SettingsPage.Values[2], 18);

  S := '{' + #13#10 +
       '  "INTERVAL_MS": ' + IntToStr(Interval * 60 * 1000) + ',' + #13#10 +
       '  "WORK_START_HOUR": ' + IntToStr(StartH) + ',' + #13#10 +
       '  "WORK_END_HOUR": ' + IntToStr(EndH) + ',' + #13#10 +
       '  "MESSAGE": "' + SettingsPage.Values[3] + '",' + #13#10 +
       '  "SUBMESSAGE": "' + SettingsPage.Values[4] + '"' + #13#10 +
       '}' + #13#10;

  if not SaveStringToFile(Path, S, False) then
    Result := False;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    WriteUserConfig();
end;
