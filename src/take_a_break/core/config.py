"""Configuration constants for take-a-break.

User overrides are read from ``%APPDATA%\\take-a-break\\config.json`` if it
exists. Any of MESSAGE, SUBMESSAGE, BUTTON_TEXT, INTERVAL_MS,
OVERLAY_DURATION_MS, WORK_START_HOUR, WORK_END_HOUR, WORK_DAYS,
HIDE_FROM_SCREEN_CAPTURE, SOUND_ENABLED, GIF_SPEED_PERCENT, BLOCKER_ALPHA may be
overridden there.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# -------- Paths --------
def _resource_root() -> Path:
    """Where bundled assets live (works for source run AND PyInstaller exe)."""
    if getattr(sys, "frozen", False):
        # PyInstaller --onefile: extracted to sys._MEIPASS
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
        # PyInstaller --onedir: assets go into "_internal/assets" (PyInstaller 6+)
        # or directly next to the exe (older versions). Check both.
        exe_dir = Path(sys.executable).parent
        if (exe_dir / "_internal" / "assets").is_dir():
            return exe_dir / "_internal"
        return exe_dir
    # Source checkout: <repo>/assets — config is now at src/take_a_break/core/config.py
    return Path(__file__).resolve().parent.parent.parent.parent


PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = _resource_root()
ASSETS_DIR = PROJECT_ROOT / "assets"
IMAGE_PATH = ASSETS_DIR / "chubby-cat.png"
WALK_GIF = ASSETS_DIR / "walking-cat.gif"

USER_CONFIG_PATH = (
    Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    / "take-a-break" / "config.json"
)

# -------- Messages --------
MESSAGE = "I see you!"
SUBMESSAGE = (
    "Get up. Look out the window. Drink some water. "
    "Don't make me get up there and sit on the keyboard!!!"
)
BUTTON_TEXT = "As you command, your furriness"

# -------- Schedule --------
INTERVAL_MS = 30 * 60 * 1000          # 30 minutes
OVERLAY_DURATION_MS = 30 * 1000       # 30 seconds
FIRST_DELAY_MS = 1500                 # ~immediate on start
WORK_START_HOUR = 9                   # 09:00
WORK_END_HOUR = 18                    # 18:00 (exclusive)
WORK_DAYS = frozenset({0, 1, 2, 3, 4})  # Mon..Fri

# How long after the overlay appears to ignore keystrokes / clicks.
# Prevents an in-flight Enter / Space / mouse click (you were typing
# or clicking when the break popped up) from dismissing it instantly.
INPUT_GRACE_MS = 700

# -------- Layout --------
POPUP_BOTTOM_MARGIN_FRAC = 0.10       # card distance from bottom of work area

# -------- Animation --------
GIF_SPEED_PERCENT = 50                # QMovie playback speed (100 = native)

# -------- Sound --------
SOUND_FILE = ASSETS_DIR / "whoosh.wav"  # optional; falls back to system chime
SOUND_ENABLED = True

# -------- Colors --------
TEXT_COLOR = "#f5e8d3"                # warm off-white
SUBTEXT_COLOR = "#b6a98f"             # muted warm gray

# Accent (warm amber — cat ginger vibe)
ACCENT = "#f5a65b"
ACCENT_HOVER = "#ffb774"
ACCENT_TEXT = "#1c1f26"

# -------- Modal blocker --------
BLOCKER_ALPHA = 0.45                  # 0.0 = invisible, 1.0 = solid black

# -------- Privacy --------
# Hide the overlay from screen capture / sharing (MS Teams, OBS, Win+Shift+S).
# You still see the cat; viewers see right through it.
HIDE_FROM_SCREEN_CAPTURE = True


# -------- User overrides ---------------------------------------------------
# Apply values from %APPDATA%\take-a-break\config.json over the defaults above.
_OVERRIDABLE = {
    "MESSAGE", "SUBMESSAGE", "BUTTON_TEXT",
    "INTERVAL_MS", "OVERLAY_DURATION_MS", "FIRST_DELAY_MS",
    "WORK_START_HOUR", "WORK_END_HOUR", "WORK_DAYS",
    "GIF_SPEED_PERCENT", "BLOCKER_ALPHA",
    "SOUND_ENABLED", "HIDE_FROM_SCREEN_CAPTURE",
}

try:
    if USER_CONFIG_PATH.is_file():
        _user = json.loads(USER_CONFIG_PATH.read_text(encoding="utf-8"))
        for _k, _v in _user.items():
            if _k in _OVERRIDABLE:
                if _k == "WORK_DAYS" and isinstance(_v, list):
                    _v = frozenset(_v)
                globals()[_k] = _v
except Exception:
    # Never let a bad user config crash the app.
    pass
