"""Mutable application state shared across modules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AppState:
    paused: bool = False
    overlays_open: bool = False
    timer: Any = None  # holds QTimer reference


STATE = AppState()
