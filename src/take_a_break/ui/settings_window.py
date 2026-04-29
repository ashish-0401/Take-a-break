"""Settings dialog — opens from the tray icon.

Lets the user change interval, work hours, and work days.
Saves to APPDATA/take-a-break/config.json and hot-reloads the scheduler.
"""
from __future__ import annotations

import json
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtWidgets import (
    QCheckBox, QDialog, QDialogButtonBox, QFormLayout,
    QGroupBox, QHBoxLayout, QLabel, QSpinBox, QVBoxLayout, QWidget,
)

from ..core import config as cfg

_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None = None, on_save: Callable[[], None] | None = None):
        super().__init__(parent)
        self.setWindowTitle("Take a Break — Settings")
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.setFixedWidth(360)
        self._on_save = on_save

        root = QVBoxLayout(self)
        root.setSpacing(16)
        root.setContentsMargins(20, 20, 20, 20)

        # ---- Interval ----
        interval_group = QGroupBox("Break interval")
        interval_layout = QFormLayout(interval_group)
        self._interval_spin = QSpinBox()
        self._interval_spin.setRange(1, 240)
        self._interval_spin.setSuffix("  minutes")
        self._interval_spin.setValue(cfg.INTERVAL_MS // 60_000)
        interval_layout.addRow("Remind me every", self._interval_spin)
        root.addWidget(interval_group)

        # ---- Work hours ----
        hours_group = QGroupBox("Work hours  (breaks only fire within this window)")
        hours_layout = QHBoxLayout(hours_group)
        hours_layout.setSpacing(8)

        self._start_spin = QSpinBox()
        self._start_spin.setRange(0, 23)
        self._start_spin.setSuffix(":00")
        self._start_spin.setValue(cfg.WORK_START_HOUR)

        self._end_spin = QSpinBox()
        self._end_spin.setRange(1, 24)
        self._end_spin.setSuffix(":00")
        self._end_spin.setValue(cfg.WORK_END_HOUR)

        hours_layout.addWidget(QLabel("From"))
        hours_layout.addWidget(self._start_spin)
        hours_layout.addWidget(QLabel("to"))
        hours_layout.addWidget(self._end_spin)
        hours_layout.addStretch()
        root.addWidget(hours_group)

        # ---- Work days ----
        days_group = QGroupBox("Active days  (breaks only fire on checked days)")
        days_layout = QVBoxLayout(days_group)
        days_layout.setSpacing(4)
        self._day_checks: list[QCheckBox] = []
        for i, name in enumerate(_DAYS):
            cb = QCheckBox(name)
            cb.setChecked(i in cfg.WORK_DAYS)
            days_layout.addWidget(cb)
            self._day_checks.append(cb)
        root.addWidget(days_group)

        # ---- Buttons ----
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _save(self) -> None:
        start = self._start_spin.value()
        end = self._end_spin.value()
        if start >= end:
            self._start_spin.setStyleSheet("border: 1px solid red;")
            self._end_spin.setStyleSheet("border: 1px solid red;")
            return

        data: dict = {
            "INTERVAL_MS": self._interval_spin.value() * 60_000,
            "WORK_START_HOUR": start,
            "WORK_END_HOUR": end,
            "WORK_DAYS": [i for i, cb in enumerate(self._day_checks) if cb.isChecked()],
        }

        # Preserve any existing keys we don't touch (MESSAGE, SUBMESSAGE, etc.)
        existing: dict = {}
        if cfg.USER_CONFIG_PATH.is_file():
            try:
                existing = json.loads(cfg.USER_CONFIG_PATH.read_text(encoding="utf-8"))
            except Exception:
                pass
        existing.update(data)

        cfg.USER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        cfg.USER_CONFIG_PATH.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Hot-reload config globals
        for k, v in data.items():
            if k == "WORK_DAYS":
                v = frozenset(v)
            setattr(cfg, k, v)

        # Notify app to restart the scheduler timer
        if self._on_save:
            self._on_save()

        self.accept()


def open_settings(on_save: Callable[[], None] | None = None) -> None:
    dlg = SettingsDialog(on_save=on_save)
    dlg.exec()
