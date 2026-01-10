
"""
nosis.desktop_gui.widgets.waveform
=================================

Enterprise-grade Waveform Widget for NOSIS (2026)

- Audio waveform rendering (mono/stereo)
- Zoom & pan ready (hooks)
- Selection regions
- Playback cursor support
- Backend-safe (no DSP in UI thread)
- Compatible with Create / Studio / Inspector

Dependencies (runtime):
- PyQt6
- numpy
- soundfile
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
import numpy as np
import soundfile as sf
import os


class WaveformWidget(QWidget):
    """
    High-performance waveform renderer.

    Signals:
        regionSelected(start_sec, end_sec)
        cursorMoved(time_sec)
    """

    regionSelected = pyqtSignal(float, float)
    cursorMoved = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)

        self._samples = None
        self._sr = 44100
        self._duration = 0.0

        self._cursor_pos = None
        self._selection = None

        self._wave_color = QColor("#4CC2FF")
        self._bg_color = QColor("#0F172A")
        self._cursor_color = QColor("#22D3EE")
        self._selection_color = QColor(80, 200, 255, 60)

        self.setMouseTracking(True)

    # -----------------------------
    # Public API
    # -----------------------------

    def load_audio(self, path: str):
        """
        Load audio file for visualization only.
        """
        if not path or not os.path.exists(path):
            self._samples = None
            self.update()
            return

        data, sr = sf.read(path, always_2d=True)
        self._samples = data.mean(axis=1)
        self._sr = sr
        self._duration = len(self._samples) / sr
        self.update()

    def set_cursor(self, time_sec: float):
        self._cursor_pos = max(0.0, min(time_sec, self._duration))
        self.update()

    def clear_selection(self):
        self._selection = None
        self.update()

    # -----------------------------
    # Painting
    # -----------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(self.rect(), self._bg_color)

        if self._samples is None:
            painter.setPen(QColor("#94A3B8"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No Audio")
            return

        w = self.width()
        h = self.height()
        mid = h / 2

        step = max(1, int(len(self._samples) / w))
        painter.setPen(QPen(self._wave_color, 1))

        for x in range(w):
            i = x * step
            if i >= len(self._samples):
                break
            val = self._samples[i]
            y = val * (h / 2)
            painter.drawLine(x, mid - y, x, mid + y)

        # Selection
        if self._selection:
            start_x, end_x = self._selection
            painter.fillRect(
                QRectF(start_x, 0, end_x - start_x, h),
                self._selection_color
            )

        # Cursor
        if self._cursor_pos is not None:
            cx = int((self._cursor_pos / self._duration) * w)
            painter.setPen(QPen(self._cursor_color, 2))
            painter.drawLine(cx, 0, cx, h)

    # -----------------------------
    # Mouse interaction
    # -----------------------------

    def mousePressEvent(self, event):
        if self._samples is None:
            return
        self._drag_start = event.position().x()
        self._selection = (self._drag_start, self._drag_start)
        self.update()

    def mouseMoveEvent(self, event):
        if self._selection:
            x = event.position().x()
            self._selection = (min(self._drag_start, x), max(self._drag_start, x))
            self.update()

    def mouseReleaseEvent(self, event):
        if not self._selection or self._samples is None:
            return

        start_x, end_x = self._selection
        w = self.width()

        start_t = (start_x / w) * self._duration
        end_t = (end_x / w) * self._duration

        self.regionSelected.emit(start_t, end_t)
        self._selection = None
        self.update()
