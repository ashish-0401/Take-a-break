# Take-a-break

A small Windows app that reminds you to take a break � a cat walks in, tells you to get up, and disappears after 30 seconds.

## Features

- Break reminder every 30 minutes during work hours (Mon�Fri, 09:00�18:00 by default).
- Walking-cat animation + a card with a message and Dismiss button.
- Works across multiple monitors � dims every screen.
- Invisible to screen sharing (Teams, Zoom, OBS) � only you see the cat.
- Settings accessible from the tray icon at any time.
- Auto-start at login (optional).

---

## Quick start (run from source)

**Requires Python 3.11+.** Download from [python.org](https://www.python.org/downloads/) � tick **"Add python.exe to PATH"** during install.

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
**Left-click** the icon ? Settings.  
**Right-click** ? Pause / Trigger break / Quit.

### Auto-start at login (optional)
```powershell
.\scripts\install_autostart.ps1            # enable
.\scripts\install_autostart.ps1 -Uninstall # disable
```

### Stop the app
```powershell
Stop-Process -Name take-a-break -Force -ErrorAction SilentlyContinue
```

---

## Settings

Left-click the tray icon to open the Settings window. You can change:

- **Interval** � how often breaks fire (default: 30 min)
- **Work hours** � start and end hour (breaks won't fire outside this window)
- **Active days** � any combination including weekends or evenings

Settings save instantly � no restart needed.

For advanced tweaks (message text, animation speed, etc.) edit `%APPDATA%\take-a-break\config.json`:

```jsonc
{
  "INTERVAL_MS": 1800000,
  "WORK_START_HOUR": 9,
  "WORK_END_HOUR": 18,
  "WORK_DAYS": [0, 1, 2, 3, 4],
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
+-- assets/                  # Cat GIF, image, sound file
+-- installer/               # Build and distribution scripts
�   +-- entry.py             # Entry point for PyInstaller
�   +-- take-a-break.spec    # PyInstaller build config
�   +-- build.ps1            # One-command build script
�   +-- installer.iss        # Inno Setup installer with settings wizard
+-- scripts/
�   +-- install_autostart.ps1
+-- src/take_a_break/
�   +-- core/                # App logic
�   �   +-- config.py        # All default settings + user config loader
�   �   +-- scheduler.py     # Work-hours-aware break timer
�   �   +-- state.py         # Shared runtime state
�   +-- ui/                  # All windows and UI
�   �   +-- overlay.py       # Blocker + cat + glass card windows
�   �   +-- settings_window.py
�   �   +-- tray.py          # System tray icon and menu
�   +-- app.py               # Startup � boots Qt, tray, scheduler
�   +-- __main__.py
+-- .github/workflows/
�   +-- release.yml          # Auto-builds installer on git tag push
+-- requirements.txt
+-- run.vbs                  # Silent launcher (no console window)
+-- pyproject.toml
```

---

## Building a redistributable installer

To share with someone who doesn't have Python � build a standalone installer locally and send the `.exe` directly (email, USB, Drive). No need to make the repo public.

**Requires:** [Inno Setup 6](https://jrsoftware.org/isdl.php) (free)

```powershell
.\installer\build.ps1
# Output: dist-installer\take-a-break-setup.exe  (~50 MB compressed)
```

The installer includes a settings wizard and registers a proper uninstaller in **Settings ? Apps**.

> **SmartScreen warning:** If you see a "Windows protected your PC" prompt on first run, click **More info → Run anyway**.

### Auto-release via GitHub Actions

```powershell
git tag v1.0.0
git push origin v1.0.0
# Installer appears at: https://github.com/ashish-0401/Take-a-break/releases/latest
```

---

## License

[MIT](LICENSE) — do whatever you want with it.
