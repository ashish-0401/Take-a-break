"""Application entry point (PySide6)."""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from . import scheduler, tray
from .overlay import show_overlay


def run() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # keep tray alive when card closes

    tray_icon = tray.build(trigger=show_overlay)
    tray_icon.show()

    scheduler.start(on_tick=show_overlay)

    sys.exit(app.exec())
