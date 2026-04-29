"""Work-hours-aware ticker (PySide6 QTimer)."""
from __future__ import annotations

from datetime import datetime
from typing import Callable

from PySide6.QtCore import QTimer

from . import config as cfg
from .state import STATE


def _is_work_time() -> bool:
    now = datetime.now()
    if now.weekday() not in cfg.WORK_DAYS:
        return False
    return cfg.WORK_START_HOUR <= now.hour < cfg.WORK_END_HOUR


def start(on_tick: Callable[[], None]) -> None:
    """Schedule break reminders during work hours."""

    def maybe_fire():
        if STATE.paused:
            return
        if not _is_work_time():
            return
        on_tick()

    timer = QTimer()
    timer.setInterval(cfg.INTERVAL_MS)
    timer.timeout.connect(maybe_fire)
    timer.start()
    STATE.timer = timer  # keep reference

    # First fire shortly after launch (still respecting work hours / pause)
    QTimer.singleShot(cfg.FIRST_DELAY_MS, maybe_fire)
