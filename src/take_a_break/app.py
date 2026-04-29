"""Application entry point (PySide6)."""
from __future__ import annotations

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from . import scheduler, tray
from .overlay import show_overlay


def _acquire_mutex() -> object | None:
    """Return a handle if we are the first instance, else None."""
    try:
        import ctypes
        handle = ctypes.windll.kernel32.CreateMutexW(None, True, "take-a-break-single-instance")
        if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            ctypes.windll.kernel32.CloseHandle(handle)
            return None
        return handle  # kept alive for process lifetime
    except Exception:
        return object()  # non-Windows: always allow


def run() -> None:
    mutex = _acquire_mutex()
    if mutex is None:
        # Another instance is already running — exit silently.
        sys.exit(0)

    app = QApplication.instance() or QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # keep tray alive when card closes

    tray_icon = tray.build(
        trigger=show_overlay,
        on_settings_saved=scheduler.reload,
    )
    tray_icon.show()

    scheduler.start(on_tick=show_overlay)

    # Trigger a break 1.5 s after launch so the user can verify it works.
    QTimer.singleShot(1500, show_overlay)

    sys.exit(app.exec())
