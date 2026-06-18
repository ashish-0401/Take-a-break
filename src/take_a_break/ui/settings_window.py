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
    QApplication, QButtonGroup, QCheckBox, QComboBox, QDialog, QDialogButtonBox,
    QFormLayout, QGroupBox, QHBoxLayout, QLabel, QMessageBox, QPushButton,
    QRadioButton, QScrollArea, QSpinBox, QVBoxLayout, QWidget,
)

from ..core import config as cfg

_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _to_12h(hour: int) -> tuple[int, str]:
    if hour == 0 or hour == 24:
        return 12, "AM"
    if hour == 12:
        return 12, "PM"
    if hour < 12:
        return hour, "AM"
    return hour - 12, "PM"


def _to_24h(hour12: int, period: str, is_end: bool = False) -> int:
    if period == "AM":
        if hour12 == 12:
            return 24 if is_end else 0
        return hour12
    if hour12 == 12:
        return 12
    return hour12 + 12


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None = None, on_save: Callable[[], None] | None = None):
        super().__init__(parent)
        self.setWindowTitle("Take a Break — Settings")
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.setMinimumWidth(360)
        self.setMinimumHeight(300)
        self.resize(380, 580)
        self._on_save = on_save

        # Top-level layout: scroll area + fixed footer.
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ---- Scrollable content area ----
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        content = QWidget()
        root = QVBoxLayout(content)
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

        # ---- Break duration ----
        # How long the overlay stays before auto-dismissing. The "Never"
        # checkbox stores 0 as the sentinel — overlay stays until ESC or
        # the dismiss button is pressed.
        duration_group = QGroupBox("Break duration")
        duration_layout = QFormLayout(duration_group)
        self._duration_spin = QSpinBox()
        self._duration_spin.setRange(5, 600)
        self._duration_spin.setSuffix("  seconds")
        # Map current ms config back to seconds; if disabled (<=0) show 30.
        self._duration_spin.setValue(
            max(5, cfg.OVERLAY_DURATION_MS // 1000) if cfg.OVERLAY_DURATION_MS > 0 else 30
        )
        self._never_close_check = QCheckBox("Never auto-close (dismiss with ESC or button only)")
        self._never_close_check.setChecked(cfg.OVERLAY_DURATION_MS <= 0)
        # When "Never" is checked, disable the duration spinbox.
        self._never_close_check.toggled.connect(
            lambda checked: self._duration_spin.setEnabled(not checked)
        )
        self._duration_spin.setEnabled(not self._never_close_check.isChecked())
        duration_layout.addRow("Auto-close after", self._duration_spin)
        duration_layout.addRow("", self._never_close_check)
        root.addWidget(duration_group)

        # ---- Work hours ----
        hours_group = QGroupBox("Work hours  (breaks only fire within this window)")
        hours_layout = QHBoxLayout(hours_group)
        hours_layout.setSpacing(8)

        self._start_spin = QSpinBox()
        self._start_spin.setRange(1, 12)
        self._start_spin.setSuffix(":00")
        start_hour12, start_period = _to_12h(cfg.WORK_START_HOUR)
        self._start_spin.setValue(start_hour12)
        self._start_ampm = QComboBox()
        self._start_ampm.addItems(["AM", "PM"])
        self._start_ampm.setCurrentText(start_period)

        self._end_spin = QSpinBox()
        self._end_spin.setRange(1, 12)
        self._end_spin.setSuffix(":00")
        end_hour12, end_period = _to_12h(cfg.WORK_END_HOUR)
        self._end_spin.setValue(end_hour12)
        self._end_ampm = QComboBox()
        self._end_ampm.addItems(["AM", "PM"])
        self._end_ampm.setCurrentText(end_period)

        hours_layout.addWidget(QLabel("From"))
        hours_layout.addWidget(self._start_spin)
        hours_layout.addWidget(self._start_ampm)
        hours_layout.addWidget(QLabel("to"))
        hours_layout.addWidget(self._end_spin)
        hours_layout.addWidget(self._end_ampm)
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

        # Finalize scrollable content.
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)  # stretch factor = 1 so scroll takes space

        # ---- Footer (always visible, outside scroll) ----
        footer = QHBoxLayout()
        footer.setContentsMargins(20, 10, 20, 10)

        # "Quit app" button — lets the user stop take-a-break without using
        # the tray right-click menu or killing the process.
        quit_btn = QPushButton("Quit app")
        quit_btn.setToolTip("Stop take-a-break completely until you launch it again")
        quit_btn.clicked.connect(self._quit_app)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        footer.addWidget(quit_btn)
        footer.addStretch()
        footer.addWidget(close_btn)

        outer.addLayout(footer)

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
        self._duration_spin.valueChanged.connect(schedule_save)
        self._never_close_check.stateChanged.connect(schedule_save)
        self._start_spin.valueChanged.connect(schedule_save)
        self._start_ampm.currentIndexChanged.connect(schedule_save)
        self._end_spin.valueChanged.connect(schedule_save)
        self._end_ampm.currentIndexChanged.connect(schedule_save)
        for cb in self._day_checks:
            cb.stateChanged.connect(schedule_save)
        self._radio_all.toggled.connect(schedule_save)
        self._radio_primary.toggled.connect(schedule_save)

    def _autosave(self) -> None:
        start = _to_24h(
            self._start_spin.value(), self._start_ampm.currentText(), is_end=False
        )
        end = _to_24h(
            self._end_spin.value(), self._end_ampm.currentText(), is_end=True
        )
        if start >= end:
            # Mark the offending fields red but don't pop a dialog — the user
            # is still adjusting. Settings stay un-saved until valid.
            self._start_spin.setStyleSheet("border: 1px solid red;")
            self._end_spin.setStyleSheet("border: 1px solid red;")
            self._start_ampm.setStyleSheet("border: 1px solid red;")
            self._end_ampm.setStyleSheet("border: 1px solid red;")
            return
        self._start_spin.setStyleSheet("")
        self._start_ampm.setStyleSheet("")
        self._end_spin.setStyleSheet("")
        self._end_ampm.setStyleSheet("")

        data: dict = {
            "INTERVAL_MS": self._interval_spin.value() * 60_000,
            "OVERLAY_DURATION_MS": (
                0 if self._never_close_check.isChecked()
                else self._duration_spin.value() * 1000
            ),
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
    cfg.reload()
    dlg = SettingsDialog(on_save=on_save)
    dlg.exec()
