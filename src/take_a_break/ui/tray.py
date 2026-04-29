"""System tray icon (PySide6)."""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter, QColor
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from ..core import config as cfg
from .settings_window import open_settings
from ..core.state import STATE


def _build_icon() -> QIcon:
    img_path = Path(cfg.IMAGE_PATH)
    if img_path.exists():
        pix = QPixmap(str(img_path))
        if not pix.isNull():
            return QIcon(pix)
    # Fallback: small amber circle
    pix = QPixmap(64, 64)
    pix.fill(QColor(0, 0, 0, 0))
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor(cfg.ACCENT))
    p.setPen(QColor(0, 0, 0, 0))
    p.drawEllipse(4, 4, 56, 56)
    p.end()
    return QIcon(pix)


def build(trigger: Callable[[], None], on_settings_saved: Callable[[], None] | None = None) -> QSystemTrayIcon:
    app = QApplication.instance()
    icon = QSystemTrayIcon(_build_icon(), parent=app)
    icon.setToolTip("Take a break")

    menu = QMenu()

    def toggle_pause():
        STATE.paused = not STATE.paused
        pause_action.setText("Resume" if STATE.paused else "Pause")

    pause_action = QAction("Pause", menu)
    pause_action.triggered.connect(toggle_pause)

    settings_action = QAction("Settings…", menu)
    settings_action.triggered.connect(lambda: open_settings(on_save=on_settings_saved))

    trigger_action = QAction("Trigger break now", menu)
    trigger_action.triggered.connect(lambda: trigger())

    quit_action = QAction("Quit", menu)
    quit_action.triggered.connect(lambda: QApplication.quit())

    menu.addAction(pause_action)
    menu.addAction(settings_action)
    menu.addAction(trigger_action)
    menu.addSeparator()
    menu.addAction(quit_action)

    icon.setContextMenu(menu)
    # Left-click -> open Settings  (right-click -> context menu as usual)
    icon.activated.connect(
        lambda reason: open_settings(on_save=on_settings_saved)
        if reason == QSystemTrayIcon.ActivationReason.Trigger else None
    )
    return icon
