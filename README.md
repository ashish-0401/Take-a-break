# Take-a-break

A tiny Windows background app that nudges you to take a break with a sassy walking cat and a glass card telling you to step away from the screen.

## Features

- Periodic break reminder during work hours (default: Mon–Fri 09:00–18:00, every 30 min).
- Walking-cat GIF + frosted-glass card with title, sub-message, and Dismiss button.
- **Multi-monitor**: dims every screen and shows the cat/card on each one.
- **Hidden from screen capture**: invisible in MS Teams / Zoom / OBS / Win+Shift+S (Win 10 2004+).
- ESC or the Dismiss button to dismiss; auto-dismiss after 30 s.
- System tray icon: Pause / Resume, Trigger break now, Quit.
- Auto-start at login via a Startup-folder shortcut.

## Project layout

```
.
├── assets/                    # cat image + walking-cat.gif + sound
├── bin/take-a-break.exe       # renamed pythonw.exe (so Task Manager shows the right name)
├── scripts/install_autostart.ps1
├── src/take_a_break/          # Python package
│   ├── app.py                 # entry point — boots QApplication, tray, scheduler
│   ├── config.py              # all knobs (interval, work hours, colors, messages)
│   ├── overlay.py             # blocker + cat + glass card windows
│   ├── scheduler.py           # work-hours-aware QTimer
│   ├── tray.py                # QSystemTrayIcon
│   └── state.py               # tiny shared dataclass
├── pyproject.toml
├── requirements.txt
└── run.vbs                    # silent launcher (no console)
```

## Install

```powershell
python -m pip install --user -r requirements.txt
```

## Start it

```powershell
# Background (silent, recommended) — appears in Task Manager as "take-a-break.exe"
wscript .\run.vbs

# Foreground (with console, useful for debugging)
$env:PYTHONPATH = "$PWD\src"; python -m take_a_break
```

## Stop it

```powershell
Stop-Process -Name take-a-break -Force -ErrorAction SilentlyContinue
```

You can also right-click the tray icon → **Quit**.

## Stop it permanently (disable autostart)

```powershell
.\scripts\install_autostart.ps1 -Uninstall
Stop-Process -Name take-a-break -Force -ErrorAction SilentlyContinue
```

To re-enable later: `.\scripts\install_autostart.ps1`

## Auto-start at login

```powershell
.\scripts\install_autostart.ps1            # install (creates Startup shortcut)
.\scripts\install_autostart.ps1 -Uninstall # remove
```

## Tweak

All settings live in [src/take_a_break/config.py](src/take_a_break/config.py): interval, work hours, message text, colors, screen-capture privacy, etc. Restart the app for changes to take effect:

```powershell
Stop-Process -Name take-a-break -Force -ErrorAction SilentlyContinue; wscript .\run.vbs
```

End-users (installed via the installer) can override settings without touching the source by editing `%APPDATA%\take-a-break\config.json`. Any of these keys are honored:

```jsonc
{
  "INTERVAL_MS": 1800000,        // 30 min
  "OVERLAY_DURATION_MS": 30000,
  "WORK_START_HOUR": 9,
  "WORK_END_HOUR": 18,
  "WORK_DAYS": [0, 1, 2, 3, 4],   // 0 = Mon
  "MESSAGE": "I see you!",
  "SUBMESSAGE": "...",
  "BUTTON_TEXT": "OK",
  "GIF_SPEED_PERCENT": 50,
  "BLOCKER_ALPHA": 0.45,
  "SOUND_ENABLED": true,
  "HIDE_FROM_SCREEN_CAPTURE": true
}
```

## Building a redistributable installer

For sharing with friends, the project ships a one-folder PyInstaller build wrapped in an Inno Setup installer (with a settings wizard).

```powershell
# 1) Build the exe (one-folder bundle in dist\take-a-break\)
.\packaging\build.ps1

# 2) Build the installer (requires Inno Setup 6 — free: https://jrsoftware.org/isdl.php)
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" packaging\installer.iss
# -> dist-installer\take-a-break-setup.exe
```

### Automated releases via GitHub Actions

A workflow at [.github/workflows/release.yml](.github/workflows/release.yml) builds both the exe and the installer on every `v*` tag push and attaches the installer to a GitHub Release:

```powershell
git tag v1.0.0
git push origin v1.0.0
# Wait ~5 min — installer appears at:
# https://github.com/<you>/<repo>/releases/latest
```

Friends download `take-a-break-setup.exe` from the Releases page and run it. The installer:

- Has a settings page (interval, work hours, message text).
- Writes them to `%APPDATA%\take-a-break\config.json`.
- Optionally adds a Startup-folder shortcut so it runs at login.
- Registers a proper uninstaller in **Settings → Apps**.

> **SmartScreen note:** unsigned `.exe`s show a "Windows protected your PC" warning the first time. Recipients click **More info → Run anyway**. Removing the warning requires a paid code-signing certificate.
