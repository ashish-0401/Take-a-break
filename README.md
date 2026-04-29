# Take-a-break

A small Windows app that reminds you to take a break — a cat walks in, tells you to get up, and disappears after 30 seconds.

## Features

- Break reminder every 30 minutes during work hours (Mon–Fri, 09:00–18:00 by default).
- Walking-cat animation + a card with a message and Dismiss button.
- Works across multiple monitors — dims every screen.
- Invisible to screen sharing (Teams, Zoom, OBS) — only you see the cat.
- Settings accessible from the tray icon at any time.
- Auto-start at login (optional, set during install).

---

## Quick start (run from source)

**You need Python 3.11+ installed.** Download it from [python.org](https://www.python.org/downloads/) — during install, tick **"Add python.exe to PATH"**.

```powershell
# 1. Clone
git clone https://github.com/ashish-0401/Take-a-break.git
cd Take-a-break

# 2. Install the one dependency
python -m pip install --user -r requirements.txt

# 3. Start (runs silently in the background)
wscript run.vbs
```

A cat icon appears in the system tray (bottom-right, may be hidden under `^`).  
**Left-click** the icon → Settings.  
**Right-click** → Pause / Trigger break / Quit.

### Optional: auto-start at login
```powershell
.\scripts\install_autostart.ps1            # enable
.\scripts\install_autostart.ps1 -Uninstall # disable
```

### Stop
```powershell
Stop-Process -Name take-a-break -Force -ErrorAction SilentlyContinue
```
Or right-click tray → **Quit**.

---

## Settings

Left-click the tray icon to open Settings. You can change:

- **Interval** — how often breaks fire (default: 30 min)
- **Work hours** — start and end hour (breaks won't fire outside this window)
- **Active days** — any combination including weekends or evenings

Settings save instantly, no restart needed.

For advanced tweaks (message text, animation speed, etc.) edit `%APPDATA%\take-a-break\config.json`:

```jsonc
{
  "INTERVAL_MS": 1800000,          // 30 min in milliseconds
  "WORK_START_HOUR": 9,
  "WORK_END_HOUR": 18,
  "WORK_DAYS": [0, 1, 2, 3, 4],   // 0=Mon, 6=Sun
  "MESSAGE": "I see you!",
  "SUBMESSAGE": "Get up. Look out the window. Drink some water.",
  "BUTTON_TEXT": "As you command, your furriness",
  "GIF_SPEED_PERCENT": 50,
  "BLOCKER_ALPHA": 0.45,
  "SOUND_ENABLED": true,
  "HIDE_FROM_SCREEN_CAPTURE": true
}
```

---

## Project layout

```
.
├── assets/          # Cat GIF, image, and sound file
├── installer/       # Everything for building the distributable
│   ├── entry.py         # Entry point used by PyInstaller
│   ├── take-a-break.spec  # PyInstaller build config
│   ├── build.ps1        # One-command build script
│   └── installer.iss    # Inno Setup installer script
├── scripts/
│   └── install_autostart.ps1  # Adds/removes Windows Startup shortcut
├── src/take_a_break/    # Python source code
│   ├── app.py           # Startup — creates tray, scheduler
│   ├── config.py        # All default settings
│   ├── overlay.py       # The cat + card windows
│   ├── scheduler.py     # Work-hours timer
│   ├── settings_window.py  # Settings dialog
│   ├── tray.py          # System tray icon and menu
│   └── state.py         # Shared state
├── .github/workflows/
│   └── release.yml      # Auto-builds installer on git tag push
├── requirements.txt     # Just PySide6
├── run.vbs              # Silent launcher (no console window)
└── pyproject.toml
```

---

## Building a redistributable installer

If you want to share this with someone without making the repo public — just build the installer locally and send the `.exe` file directly (email, USB, Google Drive, etc.).

**Requires:** [Inno Setup 6](https://jrsoftware.org/isdl.php) (free)

```powershell
.\installer\build.ps1
# Output: dist-installer\take-a-break-setup.exe  (~50 MB compressed)
```

The installer has a settings wizard (interval, work hours, active days) so the person can configure it during install, and change it anytime from the tray afterwards.

> **About the size (~109 MB installed):** the app uses Qt (PySide6) for the UI, which bundles its own rendering engine (~86 MB of DLLs). This is normal for Qt apps — VLC, OBS, and most cross-platform apps are similarly sized.

> **SmartScreen warning:** unsigned `.exe` files show a "Windows protected your PC" prompt on first run. Click **More info → Run anyway**. This is standard for any self-distributed Windows app.

### Auto-release via GitHub Actions

Tag a release and GitHub builds and publishes the installer automatically:

```powershell
git tag v1.0.0
git push origin v1.0.0
# Installer appears at: https://github.com/ashish-0401/Take-a-break/releases/latest
```


## Features

- Periodic break reminder during work hours (default: Mon–Fri 09:00–18:00, every 30 min).
- Walking-cat GIF + frosted-glass card with title, sub-message, and Dismiss button.
- **Multi-monitor**: dims every screen and shows the cat/card on each one.
- **Hidden from screen capture**: invisible in MS Teams / Zoom / OBS / Win+Shift+S (Win 10 2004+).
- ESC or the Dismiss button to dismiss; auto-dismiss after 30 s.
- System tray icon: Pause / Resume, Trigger break now, Quit.
- Auto-start at login via a Startup-folder shortcut.

---

## Prerequisites (before you clone)

| Requirement | Version | How to get it |
|---|---|---|
| Windows | 10 or 11 | — |
| Python | 3.11 or later | [python.org/downloads](https://www.python.org/downloads/) — tick **"Add python.exe to PATH"** during install |
| Git | any recent | [git-scm.com](https://git-scm.com/) (optional — only needed if cloning) |

Verify Python is installed and on PATH:
```powershell
python --version   # should print Python 3.11.x or higher
```

---

## Getting started (run from source)

### 1. Clone the repo
```powershell
git clone https://github.com/ashish-0401/Take-a-break.git
cd Take-a-break
```

### 2. Install dependencies
```powershell
python -m pip install --user -r requirements.txt
```
This installs **PySide6** (Qt for Python) — about 80 MB, one-time.

### 3. Start the app
```powershell
wscript run.vbs
```
The app starts silently in the background. A cat tray icon appears in the system tray (bottom-right). First break fires after ~30 min (during work hours).

### 4. Auto-start at login (optional)
```powershell
.\scripts\install_autostart.ps1
```
Creates a shortcut in your Windows Startup folder so the app launches automatically when you log in.

To remove it later:
```powershell
.\scripts\install_autostart.ps1 -Uninstall
```

---

## Stopping the app

```powershell
Stop-Process -Name take-a-break -Force -ErrorAction SilentlyContinue
```

Or right-click the tray icon → **Quit**.

---

## Project layout

```
.
├── assets/                    # cat PNG, walking-cat GIF, optional sound
├── packaging/
│   ├── build.ps1              # local PyInstaller build script
│   ├── entry.py               # frozen entry point for PyInstaller
│   ├── installer.iss          # Inno Setup installer script (settings wizard)
│   └── take-a-break.spec      # PyInstaller spec
├── scripts/
│   └── install_autostart.ps1  # adds/removes Windows Startup shortcut
├── src/take_a_break/
│   ├── app.py                 # entry point — boots QApplication, tray, scheduler
│   ├── config.py              # all knobs (interval, work hours, colors, messages)
│   ├── overlay.py             # blocker + cat + glass card windows
│   ├── scheduler.py           # work-hours-aware QTimer
│   ├── tray.py                # QSystemTrayIcon
│   └── state.py               # tiny shared dataclass
├── .github/workflows/
│   └── release.yml            # auto-build installer on git tag push
├── pyproject.toml
├── requirements.txt
└── run.vbs                    # silent launcher (no console window)
```

---

## Customise

Right-click the tray icon → **Settings** to change your schedule at any time:

- **Interval** — how often breaks fire
- **Work hours** — start and end hour (breaks won't fire outside this window)
- **Active days** — any combination of Mon–Sun (check Saturday/Sunday to use it on weekends or evenings)

Settings are saved to `%APPDATA%\take-a-break\config.json` and take effect immediately — no restart needed.

Advanced users can also edit that JSON file directly. Supported keys:

```jsonc
{
  "INTERVAL_MS": 1800000,
  "WORK_START_HOUR": 9,
  "WORK_END_HOUR": 18,
  "WORK_DAYS": [0, 1, 2, 3, 4],   // 0=Mon … 6=Sun
  "MESSAGE": "I see you!",
  "SUBMESSAGE": "Get up. Look out the window. Drink some water.",
  "BUTTON_TEXT": "As you command, your furriness",
  "GIF_SPEED_PERCENT": 50,
  "BLOCKER_ALPHA": 0.45,
  "SOUND_ENABLED": true,
  "HIDE_FROM_SCREEN_CAPTURE": true
}
```

---

## Building a redistributable installer

If you want to share this with someone who doesn't have Python installed, you can build a standalone `.exe` installer. It bundles everything — no setup needed on the other machine.

The installer includes a settings wizard (interval, work hours, active days) so the person can configure it during install. They can also change settings anytime via the tray icon afterwards.

**You don't need to make the repo public.** Just build the installer locally and send the `.exe` file via email, Google Drive, USB, or any file-sharing tool.

### Prerequisites
- [Inno Setup 6](https://jrsoftware.org/isdl.php) (free — install it, then run the build script below)

### Build
```powershell
.\packaging\build.ps1
# Output: dist-installer\take-a-break-setup.exe
```

That single script installs PyInstaller, builds the exe bundle, finds Inno Setup automatically, and produces the installer. Works whether Inno Setup is installed system-wide or per-user.

### Auto-release via GitHub Actions

Tag a release and GitHub builds + attaches the installer automatically:

```powershell
git tag v1.0.0
git push origin v1.0.0
# Installer appears at: https://github.com/ashish-0401/Take-a-break/releases/latest
```

> **Note:** Unsigned executables show a Windows SmartScreen warning on first run. Click **More info → Run anyway** to proceed. This is normal for any free indie Windows app.


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
