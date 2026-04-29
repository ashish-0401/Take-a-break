"""Break-reminder overlay built with PySide6.

- BlockerWindow: per-screen translucent dim layer that absorbs input.
- CatWindow: frameless transparent window that plays the walking-cat GIF.
- GlassCard: frameless translucent card with title, subtitle, and dismiss button.

ESC or the Dismiss button closes everything; auto-dismisses after a configured
duration.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import (
    QGuiApplication, QMovie, QPixmap, QColor, QPainter, QKeyEvent, QCursor,
)
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QFrame,
)

from . import config as cfg
from .state import STATE

# Optional sound (Windows built-in)
try:
    import winsound
except Exception:  # pragma: no cover
    winsound = None


def _exclude_from_capture(widget: QWidget) -> None:
    """Make a window invisible to screen capture / sharing (Windows only).

    Uses SetWindowDisplayAffinity with WDA_EXCLUDEFROMCAPTURE (Win 10 2004+).
    Tools like MS Teams, OBS, Win+Shift+S see a transparent hole instead.
    """
    if not cfg.HIDE_FROM_SCREEN_CAPTURE:
        return
    try:
        import ctypes
        hwnd = int(widget.winId())
        WDA_EXCLUDEFROMCAPTURE = 0x11
        ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
    except Exception:
        pass


# ----- Currently-open windows (so they aren't garbage collected) -----
_open_windows: list[QWidget] = []


def _play_sound() -> None:
    if not cfg.SOUND_ENABLED or winsound is None:
        return
    try:
        if Path(cfg.SOUND_FILE).exists():
            winsound.PlaySound(
                str(cfg.SOUND_FILE),
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
            )
        else:
            winsound.PlaySound(
                "SystemAsterisk",
                winsound.SND_ALIAS | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
            )
    except Exception:
        pass


# ============================================================
# Blocker — absorbs all input, dims the screen.
# ============================================================
class BlockerWindow(QWidget):
    def __init__(self, screen):
        super().__init__()
        # Bind this top-level to the target screen BEFORE setGeometry,
        # so DPI-aware geometry maps correctly on multi-monitor setups.
        self.setScreen(screen)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self._dim = QColor(0, 0, 0, int(cfg.BLOCKER_ALPHA * 255))
        self.setGeometry(screen.geometry())

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), self._dim)

    def mousePressEvent(self, event):
        # Swallow the click without stealing focus/activation.
        event.accept()


# ============================================================
# Cat — plays the walking GIF natively via QMovie.
# ============================================================
class CatWindow(QWidget):
    def __init__(self, screen):
        super().__init__()
        self.setScreen(screen)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

        avail = screen.availableGeometry()
        self.setGeometry(avail)

        self._label = QLabel(self)
        self._label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._label.setStyleSheet("background: transparent;")
        self._label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        gif = Path(cfg.WALK_GIF)
        if gif.exists():
            movie = QMovie(str(gif))
            # Determine target size from first frame so we can fit fully.
            movie.jumpToFrame(0)
            src = movie.currentImage().size()
            if src.isValid() and src.width() > 0:
                scale = min(avail.width() / src.width(), avail.height() / src.height())
                target = QSize(int(src.width() * scale), int(src.height() * scale))
                movie.setScaledSize(target)
                self._label.setFixedSize(target)
            self._label.setMovie(movie)
            movie.setSpeed(cfg.GIF_SPEED_PERCENT)
            # Cache frames so QMovie doesn't redecode the GIF on every loop.
            movie.setCacheMode(QMovie.CacheMode.CacheAll)
            movie.start()
            self._movie = movie
        else:
            # Fallback: still PNG
            still = Path(cfg.IMAGE_PATH)
            if still.exists():
                pix = QPixmap(str(still))
                pix = pix.scaled(
                    avail.size() * 0.6,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self._label.setPixmap(pix)
                self._label.setFixedSize(pix.size())

        # Center the label horizontally, top-align.
        self._label.move((avail.width() - self._label.width()) // 2, 0)


# ============================================================
# Glass Card — modern glassmorphism with translucent background,
# rounded corners, soft shadow, hover-animated button.
# ============================================================
class GlassCard(QWidget):
    def __init__(self, on_dismiss):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self._on_dismiss = on_dismiss

        # Outer container -> NO margins, otherwise the empty space shows the
        # dim blocker behind, looking like a second card.
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # Inner card
        self._card = QFrame()
        self._card.setObjectName("card")
        self._card.setStyleSheet(self._qss())
        # Note: no QGraphicsDropShadowEffect — it paints a soft halo whose
        # rounded edge sits outside the card, which reads as a second card.

        inner = QVBoxLayout(self._card)
        inner.setContentsMargins(40, 30, 40, 28)
        inner.setSpacing(0)

        title = QLabel(cfg.MESSAGE)
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)

        sub = QLabel(cfg.SUBMESSAGE)
        sub.setObjectName("sub")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)

        self._btn = QPushButton(cfg.BUTTON_TEXT)
        self._btn.setObjectName("btn")
        self._btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn.clicked.connect(self._on_button)
        # Don't let the button be the keyboard-focus target. Otherwise an
        # in-flight Enter/Space keypress (the user was typing when the
        # overlay appeared) instantly "clicks" it and dismisses the break.
        self._btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Make the card itself the focus target so ESC still works, but
        # no widget reacts to Enter/Space.
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Grace period: ignore all input for the first cfg.INPUT_GRACE_MS
        # so keystrokes/clicks already in flight when the overlay appears
        # don't dismiss it.
        self._accepting_input = False
        QTimer.singleShot(
            cfg.INPUT_GRACE_MS,
            lambda: setattr(self, "_accepting_input", True),
        )

        hint = QLabel("ESC to dismiss")
        hint.setObjectName("hint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

        inner.addWidget(title)
        inner.addSpacing(10)
        inner.addWidget(sub)
        inner.addSpacing(22)
        inner.addWidget(self._btn, alignment=Qt.AlignmentFlag.AlignCenter)
        inner.addSpacing(14)
        inner.addWidget(hint)

        outer.addWidget(self._card)

        # Card sizing — let it fit its content within reasonable bounds.
        self._card.setMaximumWidth(640)
        self._card.setMinimumWidth(440)

        self._fade_in()

    def _dismiss(self):
        self._on_dismiss()

    def _on_button(self):
        # Swallow clicks during the grace period so a stray click doesn't
        # close the overlay before the user has even seen it.
        if not self._accepting_input:
            return
        self._dismiss()

    def keyPressEvent(self, event: QKeyEvent):
        if not self._accepting_input:
            event.accept()
            return
        if event.key() == Qt.Key.Key_Escape:
            self._dismiss()
        else:
            super().keyPressEvent(event)

    def _fade_in(self):
        self.setWindowOpacity(0.0)
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(420)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.start()

    @staticmethod
    def _qss() -> str:
        # Real glassmorphism — translucent background, white border,
        # subtle inner highlights via gradients on title/button.
        return f"""
        QFrame#card {{
            background: rgba(62, 44, 28, 0.95);
        }}

        QLabel#title {{
            color: {cfg.TEXT_COLOR};
            font-family: 'Segoe UI', sans-serif;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: 0.3px;
        }}

        QLabel#sub {{
            color: {cfg.SUBTEXT_COLOR};
            font-family: 'Segoe UI', sans-serif;
            font-size: 16px;
            line-height: 1.4;
        }}

        QPushButton#btn {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {cfg.ACCENT_HOVER}, stop:1 {cfg.ACCENT});
            color: {cfg.ACCENT_TEXT};
            font-family: 'Segoe UI Semibold', 'Segoe UI', sans-serif;
            font-size: 12px;
            font-weight: 600;
            padding: 10px 28px;
            border: none;
            border-radius: 5px;
            min-width: 160px;
        }}
        QPushButton#btn:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffc88a, stop:1 {cfg.ACCENT_HOVER});
        }}
        QPushButton#btn:pressed {{
            background: {cfg.ACCENT};
        }}

        QLabel#hint {{
            color: rgba(255, 255, 255, 0.40);
            font-family: 'Segoe UI', sans-serif;
            font-size: 10px;
        }}
        """


# ============================================================
# Public entry: show_overlay()
# ============================================================
# Tracked auto-dismiss timer. Kept as a module-level handle so an early
# dismiss (ESC / button) can stop() it. Otherwise, when INTERVAL_MS is
# shorter than OVERLAY_DURATION_MS, a stale auto-dismiss from a prior
# overlay would fire and close the *current* overlay early.
_auto_dismiss_timer: QTimer | None = None


def _close_all():
    global _auto_dismiss_timer
    if _auto_dismiss_timer is not None:
        _auto_dismiss_timer.stop()
        _auto_dismiss_timer = None
    if not STATE.overlays_open:
        return
    STATE.overlays_open = False
    while _open_windows:
        w = _open_windows.pop()
        try:
            w.close()
            w.deleteLater()
        except Exception:
            pass


def show_overlay() -> None:
    """Show the break overlay (cat + glass card) on every screen."""
    global _auto_dismiss_timer
    if STATE.overlays_open:
        return
    STATE.overlays_open = True

    _play_sound()

    screens = QGuiApplication.screens()

    # One blocker, cat, and card per screen.
    blockers: list[BlockerWindow] = []
    cats: list[CatWindow] = []
    cards: list[GlassCard] = []

    for screen in screens:
        blockers.append(BlockerWindow(screen))
        cats.append(CatWindow(screen))
        card = GlassCard(on_dismiss=_close_all)
        card.setScreen(screen)
        cards.append(card)

    # Show blockers first (lowest z), then cats, then cards on top.
    for b, s in zip(blockers, screens):
        b.show()
        b.setGeometry(s.geometry())
        b.raise_()
        _exclude_from_capture(b)

    for cat, s in zip(cats, screens):
        cat.setGeometry(s.availableGeometry())
        cat.show()
        cat.raise_()
        _exclude_from_capture(cat)

    # Position cards near the bottom-center of each screen's work area.
    for card, s in zip(cards, screens):
        card.adjustSize()
        avail = s.availableGeometry()
        size = card.sizeHint()
        cw = max(size.width(), card.minimumWidth())
        ch = size.height()
        cx = avail.x() + (avail.width() - cw) // 2
        cy = avail.y() + avail.height() - ch - int(avail.height() * cfg.POPUP_BOTTOM_MARGIN_FRAC)
        card.setGeometry(cx, cy, cw, ch)
        card.show()
        card.raise_()
        _exclude_from_capture(card)

    # Focus the card on the screen under the cursor (so ESC works there).
    active = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
    try:
        idx = screens.index(active)
        cards[idx].activateWindow()
        cards[idx].setFocus()
    except (ValueError, IndexError):
        if cards:
            cards[0].activateWindow()
            cards[0].setFocus()

    _open_windows.extend(blockers)
    _open_windows.extend(cats)
    _open_windows.extend(cards)

    # Auto-dismiss — tracked so an early dismiss can cancel it (otherwise
    # a stale timer from this show would later close a future overlay).
    _auto_dismiss_timer = QTimer()
    _auto_dismiss_timer.setSingleShot(True)
    _auto_dismiss_timer.timeout.connect(_close_all)
    _auto_dismiss_timer.start(cfg.OVERLAY_DURATION_MS)
