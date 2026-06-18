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
; Always launch silently after Finish — the scheduler only runs while the
; app process is alive, so we want it running immediately after install
; (no "Launch now" checkbox to forget to tick).
Filename: "{app}\{#AppExeName}"; Flags: nowait runhidden skipifsilent

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
  SettingsPage: TWizardPage;
  DaysPage: TWizardPage;
  IntervalEdit: TEdit;
  StartHourCombo: TComboBox;
  StartAmRadio: TRadioButton;
  StartPmRadio: TRadioButton;
  EndHourCombo: TComboBox;
  EndAmRadio: TRadioButton;
  EndPmRadio: TRadioButton;
  DurationEdit: TEdit;
  DayChecks: array[0..6] of TCheckBox;
  ScreenAllRadio: TRadioButton;
  ScreenPrimaryRadio: TRadioButton;

procedure InitializeWizard;
var
  DayNames: array[0..6] of String;
  i: Integer;
  lbl: TLabel;
begin
  // Page 1: interval + work hours
  SettingsPage := CreateCustomPage(
    wpSelectTasks,
    'Break Settings',
    'Set up your break schedule'
  );

  lbl := TLabel.Create(SettingsPage);
  lbl.Parent := SettingsPage.Surface;
  lbl.Caption := 'You can change these anytime from the tray icon → Settings.';
  lbl.Left := 0;
  lbl.Top := 8;
  lbl.Width := 380;

  lbl := TLabel.Create(SettingsPage);
  lbl.Parent := SettingsPage.Surface;
  lbl.Caption := 'Interval (minutes between breaks):';
  lbl.Left := 0;
  lbl.Top := 32;
  lbl.Width := 220;

  IntervalEdit := TEdit.Create(SettingsPage);
  IntervalEdit.Parent := SettingsPage.Surface;
  IntervalEdit.Left := 230;
  IntervalEdit.Top := 28;
  IntervalEdit.Width := 100;
  IntervalEdit.Text := '30';

  lbl := TLabel.Create(SettingsPage);
  lbl.Parent := SettingsPage.Surface;
  lbl.Caption := 'Work start time:';
  lbl.Left := 0;
  lbl.Top := 64;
  lbl.Width := 220;

  StartHourCombo := TComboBox.Create(SettingsPage);
  StartHourCombo.Parent := SettingsPage.Surface;
  StartHourCombo.Left := 230;
  StartHourCombo.Top := 60;
  StartHourCombo.Width := 60;
  StartHourCombo.Style := csDropDownList;
  for i := 1 to 12 do
    StartHourCombo.Items.Add(IntToStr(i));
  StartHourCombo.ItemIndex := 8; // default 9

  StartAmRadio := TRadioButton.Create(SettingsPage);
  StartAmRadio.Parent := SettingsPage.Surface;
  StartAmRadio.Caption := 'AM';
  StartAmRadio.Left := 300;
  StartAmRadio.Top := 60;
  StartAmRadio.Width := 40;
  StartAmRadio.Checked := True;

  StartPmRadio := TRadioButton.Create(SettingsPage);
  StartPmRadio.Parent := SettingsPage.Surface;
  StartPmRadio.Caption := 'PM';
  StartPmRadio.Left := 345;
  StartPmRadio.Top := 60;
  StartPmRadio.Width := 40;

  lbl := TLabel.Create(SettingsPage);
  lbl.Parent := SettingsPage.Surface;
  lbl.Caption := 'Work end time:';
  lbl.Left := 0;
  lbl.Top := 100;
  lbl.Width := 220;

  EndHourCombo := TComboBox.Create(SettingsPage);
  EndHourCombo.Parent := SettingsPage.Surface;
  EndHourCombo.Left := 230;
  EndHourCombo.Top := 96;
  EndHourCombo.Width := 60;
  EndHourCombo.Style := csDropDownList;
  for i := 1 to 12 do
    EndHourCombo.Items.Add(IntToStr(i));
  EndHourCombo.ItemIndex := 5; // default 6

  EndAmRadio := TRadioButton.Create(SettingsPage);
  EndAmRadio.Parent := SettingsPage.Surface;
  EndAmRadio.Caption := 'AM';
  EndAmRadio.Left := 300;
  EndAmRadio.Top := 96;
  EndAmRadio.Width := 40;

  EndPmRadio := TRadioButton.Create(SettingsPage);
  EndPmRadio.Parent := SettingsPage.Surface;
  EndPmRadio.Caption := 'PM';
  EndPmRadio.Left := 345;
  EndPmRadio.Top := 96;
  EndPmRadio.Width := 40;
  EndPmRadio.Checked := True;

  lbl := TLabel.Create(SettingsPage);
  lbl.Parent := SettingsPage.Surface;
  lbl.Caption := 'Auto-close after (seconds, 0 = never):';
  lbl.Left := 0;
  lbl.Top := 136;
  lbl.Width := 220;

  DurationEdit := TEdit.Create(SettingsPage);
  DurationEdit.Parent := SettingsPage.Surface;
  DurationEdit.Left := 230;
  DurationEdit.Top := 132;
  DurationEdit.Width := 100;
  DurationEdit.Text := '30';

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

  // "Show break on" — primary monitor only vs all monitors.
  lbl := TLabel.Create(DaysPage);
  lbl.Parent := DaysPage.Surface;
  lbl.Caption := 'Show break on:';
  lbl.Left := 0;
  lbl.Top := 7 * 28 + 12;
  lbl.Font.Style := [fsBold];

  ScreenAllRadio := TRadioButton.Create(DaysPage);
  ScreenAllRadio.Parent := DaysPage.Surface;
  ScreenAllRadio.Caption := 'All screens';
  ScreenAllRadio.Left := 0;
  ScreenAllRadio.Top := 7 * 28 + 36;
  ScreenAllRadio.Width := 220;
  ScreenAllRadio.Checked := True;

  ScreenPrimaryRadio := TRadioButton.Create(DaysPage);
  ScreenPrimaryRadio.Parent := DaysPage.Surface;
  ScreenPrimaryRadio.Caption := 'Primary screen only';
  ScreenPrimaryRadio.Left := 0;
  ScreenPrimaryRadio.Top := 7 * 28 + 60;
  ScreenPrimaryRadio.Width := 220;
end;

function ParseTimeCombo(const HourText: string; const IsPm: Boolean; const IsEnd: Boolean): Integer;
var
  Hour: Integer;
begin
  Hour := StrToIntDef(HourText, 12);
  if (Hour < 1) or (Hour > 12) then
    Hour := 12;

  if not IsPm then
  begin
    if Hour = 12 then
    begin
      if IsEnd then
        Result := 24
      else
        Result := 0;
    end
    else
      Result := Hour;
  end
  else
  begin
    if Hour = 12 then
      Result := 12
    else
      Result := Hour + 12;
  end;
end;

function WriteUserConfig(): Boolean;
var
  Dir, Path, DayList, S, ShowAll: string;
  Interval, StartH, EndH, Duration, i: Integer;
  First: Boolean;
begin
  Result := True;
  Dir := ExpandConstant('{userappdata}\take-a-break');
  if not DirExists(Dir) then ForceDirectories(Dir);
  Path := Dir + '\config.json';

  Interval := StrToIntDef(IntervalEdit.Text, 30);
  StartH   := ParseTimeCombo(StartHourCombo.Text, StartPmRadio.Checked, False);
  EndH     := ParseTimeCombo(EndHourCombo.Text, EndPmRadio.Checked, True);
  Duration := StrToIntDef(DurationEdit.Text, 30);

  if ScreenAllRadio.Checked then
    ShowAll := 'true'
  else
    ShowAll := 'false';

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
       '  "OVERLAY_DURATION_MS": ' + IntToStr(Duration * 1000) + ',' + #13#10 +
       '  "WORK_START_HOUR": ' + IntToStr(StartH) + ',' + #13#10 +
       '  "WORK_END_HOUR": ' + IntToStr(EndH) + ',' + #13#10 +
       '  "WORK_DAYS": [' + DayList + '],' + #13#10 +
       '  "SHOW_ON_ALL_SCREENS": ' + ShowAll + #13#10 +
       '}' + #13#10;

  if not SaveStringToFile(Path, S, False) then
    Result := False;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    WriteUserConfig();
end;
