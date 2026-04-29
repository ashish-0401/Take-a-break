; Inno Setup script for take-a-break.
; Build with:   "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" packaging\installer.iss
; Inno Setup is free: https://jrsoftware.org/isdl.php

#define AppName     "Take a Break"
#define AppId       "{{8E4F2C30-7A1E-4D0A-9F44-CA1234567890}"
#define AppVersion  "1.0.0"
#define AppPublisher "Ashish Jaiswal"
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
  DaysPage: TWizardPage;
  DayChecks: array[0..6] of TCheckBox;

procedure InitializeWizard;
var
  DayNames: array[0..6] of String;
  i: Integer;
  lbl: TLabel;
begin
  // Page 1: interval + work hours
  SettingsPage := CreateInputQueryPage(
    wpSelectTasks,
    'Break Settings',
    'Set up your break schedule',
    'You can change these anytime from the tray icon → Settings.'
  );
  SettingsPage.Add('Interval (minutes between breaks):', False);
  SettingsPage.Add('Work start hour (0–23):', False);
  SettingsPage.Add('Work end hour (1–24):', False);
  SettingsPage.Values[0] := '30';
  SettingsPage.Values[1] := '9';
  SettingsPage.Values[2] := '18';

  // Page 2: work days checkboxes
  DaysPage := CreateCustomPage(
    SettingsPage.ID,
    'Active Days',
    'Breaks only fire on the days you check.'
  );

  DayNames[0] := 'Monday';
  DayNames[1] := 'Tuesday';
  DayNames[2] := 'Wednesday';
  DayNames[3] := 'Thursday';
  DayNames[4] := 'Friday';
  DayNames[5] := 'Saturday';
  DayNames[6] := 'Sunday';

  for i := 0 to 6 do
  begin
    DayChecks[i] := TCheckBox.Create(DaysPage);
    DayChecks[i].Parent := DaysPage.Surface;
    DayChecks[i].Caption := DayNames[i];
    DayChecks[i].Left := 0;
    DayChecks[i].Top := i * 28;
    DayChecks[i].Width := 200;
    DayChecks[i].Checked := (i <= 4); // Mon-Fri default
  end;
end;

function WriteUserConfig(): Boolean;
var
  Dir, Path, DayList, S: string;
  Interval, StartH, EndH, i: Integer;
  First: Boolean;
begin
  Result := True;
  Dir := ExpandConstant('{userappdata}\take-a-break');
  if not DirExists(Dir) then ForceDirectories(Dir);
  Path := Dir + '\config.json';

  Interval := StrToIntDef(SettingsPage.Values[0], 30);
  StartH   := StrToIntDef(SettingsPage.Values[1], 9);
  EndH     := StrToIntDef(SettingsPage.Values[2], 18);

  // Build WORK_DAYS array
  DayList := '';
  First := True;
  for i := 0 to 6 do
  begin
    if DayChecks[i].Checked then
    begin
      if not First then DayList := DayList + ', ';
      DayList := DayList + IntToStr(i);
      First := False;
    end;
  end;

  S := '{' + #13#10 +
       '  "INTERVAL_MS": ' + IntToStr(Interval * 60 * 1000) + ',' + #13#10 +
       '  "WORK_START_HOUR": ' + IntToStr(StartH) + ',' + #13#10 +
       '  "WORK_END_HOUR": ' + IntToStr(EndH) + ',' + #13#10 +
       '  "WORK_DAYS": [' + DayList + ']' + #13#10 +
       '}' + #13#10;

  if not SaveStringToFile(Path, S, False) then
    Result := False;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    WriteUserConfig();
end;
