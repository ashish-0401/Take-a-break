"""Settings dialog — opens from the tray icon.

Lets the user change interval, work hours, and work days.
Saves to APPDATA/take-a-break/config.json and hot-reloads the scheduler.
"""
from __future__ import annotations

import json
from typing import Callable

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QCheckBox, QDialog, QDialogButtonBox,
    QFormLayout, QGroupBox, QHBoxLayout, QLabel, QMessageBox, QPushButton,
    QRadioButton, QSpinBox, QVBoxLayout, QWidget,
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

        # ---- Show on (primary vs all screens) ----
        screens_group = QGroupBox("Show break on")
        screens_layout = QVBoxLayout(screens_group)
        screens_layout.setSpacing(4)
        self._radio_all = QRadioButton("All screens")
        self._radio_primary = QRadioButton("Primary screen only")
        if cfg.SHOW_ON_ALL_SCREENS:
            self._radio_all.setChecked(True)
        else:
            self._radio_primary.setChecked(True)
        # Group them so they're mutually exclusive.
        self._screens_group = QButtonGroup(self)
        self._screens_group.addButton(self._radio_all)
        self._screens_group.addButton(self._radio_primary)
        screens_layout.addWidget(self._radio_all)
        screens_layout.addWidget(self._radio_primary)
        root.addWidget(screens_group)

        # ---- Buttons ----
        # No Save button — every change auto-saves (debounced 200 ms below).
        # Closing the dialog (X / Esc / Close) is sufficient to dismiss it;
        # nothing is lost on close.
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        close_btn = buttons.button(QDialogButtonBox.StandardButton.Close)
        if close_btn is not None:
            close_btn.clicked.connect(self.accept)

        # "Quit app" button — lets the user stop take-a-break without using
        # the tray right-click menu or killing the process.
        quit_btn = QPushButton("Quit app")
        quit_btn.setToolTip("Stop take-a-break completely until you launch it again")
        quit_btn.clicked.connect(self._quit_app)
        buttons.addButton(quit_btn, QDialogButtonBox.ButtonRole.DestructiveRole)

        root.addWidget(buttons)

        # ---- Auto-save plumbing ----
        # Debounce so a spinbox click that bumps the value 5 times in a
        # second doesn't write to disk 5 times.
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(200)
        self._save_timer.timeout.connect(self._autosave)

        def schedule_save(*_args):
            self._save_timer.start()

        # Hook every control's change signal.
        self._interval_spin.valueChanged.connect(schedule_save)
        self._start_spin.valueChanged.connect(schedule_save)
        self._end_spin.valueChanged.connect(schedule_save)
        for cb in self._day_checks:
            cb.stateChanged.connect(schedule_save)
        self._radio_all.toggled.connect(schedule_save)
        self._radio_primary.toggled.connect(schedule_save)

    def _autosave(self) -> None:
        start = self._start_spin.value()
        end = self._end_spin.value()
        if start >= end:
            # Mark the offending fields red but don't pop a dialog — the user
            # is still adjusting. Settings stay un-saved until valid.
            self._start_spin.setStyleSheet("border: 1px solid red;")
            self._end_spin.setStyleSheet("border: 1px solid red;")
            return
        self._start_spin.setStyleSheet("")
        self._end_spin.setStyleSheet("")

        data: dict = {
            "INTERVAL_MS": self._interval_spin.value() * 60_000,
            "WORK_START_HOUR": start,
            "WORK_END_HOUR": end,
            "WORK_DAYS": [i for i, cb in enumerate(self._day_checks) if cb.isChecked()],
            "SHOW_ON_ALL_SCREENS": self._radio_all.isChecked(),
        }

        # Preserve any existing keys we don't touch (MESSAGE, SUBMESSAGE, etc.)
        existing: dict = {}
        if cfg.USER_CONFIG_PATH.is_file():
            try:
                existing = json.loads(cfg.USER_CONFIG_PATH.read_text(encoding="utf-8"))
            except Exception:
                pass
        existing.update(data)

        try:
            cfg.USER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            cfg.USER_CONFIG_PATH.write_text(
                json.dumps(existing, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Take a Break — save failed",
                f"Could not save settings:\n\n{e}",
            )
            return

        # Hot-reload config globals
        for k, v in data.items():
            if k == "WORK_DAYS":
                v = frozenset(v)
            setattr(cfg, k, v)

        # Notify app to restart the scheduler timer
        if self._on_save:
            self._on_save()

    def _quit_app(self) -> None:
        QApplication.quit()


def open_settings(on_save: Callable[[], None] | None = None) -> None:
    dlg = SettingsDialog(on_save=on_save)
    dlg.exec()
