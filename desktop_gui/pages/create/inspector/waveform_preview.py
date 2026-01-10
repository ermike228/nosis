"""
NOSIS – Waveform Preview
=======================

Enterprise-grade audio waveform visualization for Inspector Panel (2025–2026).

Purpose:
- Visual summary of generated audio
- Immediate understanding of dynamics, density and structure
- Anchor for navigation, QA and regeneration decisions
- Bridge between Create workflow and Studio timeline

WaveformPreview is NOT a decoration.
It is a cognitive tool for music professionals.
"""

from __future__ import annotations

import logging
import wave
import struct
from typing import Optional, List

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import QFrame

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.waveform_preview")


class WaveformPreview(QFrame):
    """
    Lightweight, realtime-safe waveform preview widget.

    Responsibilities:
    - Load audio file metadata safely
    - Render waveform preview efficiently
    - Support selection, hover and navigation hooks
    - Emit intent-based events (no DSP here)
    """

    waveform_clicked = pyqtSignal(float)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()

        self._audio_path: Optional[str] = None
        self._samples: List[float] = []
        self._duration: float = 0.0

        self.setObjectName("WaveformPreview")
        self.setMinimumHeight(80)
        self.setMaximumHeight(120)

        self.setMouseTracking(True)

        logger.info("WaveformPreview initialized")

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def set_audio(self, audio_path: Optional[str]) -> None:
        """
        Load audio file and prepare waveform samples.
        Heavy DSP is intentionally avoided.
        """
        self._audio_path = audio_path
        self._samples.clear()
        self._duration = 0.0

        if not audio_path:
            self.update()
            return

        try:
            with wave.open(audio_path, "rb") as wf:
                n_frames = wf.getnframes()
                framerate = wf.getframerate()
                channels = wf.getnchannels()

                self._duration = n_frames / float(framerate)

                raw = wf.readframes(n_frames)
                fmt = "<" + "h" * (len(raw) // 2)
                samples = struct.unpack(fmt, raw)

                # Downsample aggressively for UI safety
                step = max(1, len(samples) // 1000)
                for i in range(0, len(samples), step * channels):
                    self._samples.append(abs(samples[i]) / 32768.0)

        except Exception as e:
            logger.error("Failed to load waveform: %s", e)
            self._samples.clear()

        self.update()

    # ------------------------------------------------------------------
    # PAINT
    # ------------------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        mid_y = rect.height() / 2

        painter.fillRect(rect, QColor("#111111"))

        if not self._samples:
            painter.setPen(QColor("#666666"))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "No audio")
            return

        pen = QPen(QColor("#3aa0ff"))
        pen.setWidth(1)
        painter.setPen(pen)

        width = rect.width()
        height = rect.height()

        step = max(1, len(self._samples) // width)

        x = 0
        for i in range(0, len(self._samples), step):
            amp = self._samples[i]
            y = amp * (height / 2)
            painter.drawLine(x, mid_y - y, x, mid_y + y)
            x += 1
            if x > width:
                break

    # ------------------------------------------------------------------
    # INTERACTION
    # ------------------------------------------------------------------

    def mousePressEvent(self, event):
        if not self._duration:
            return

        pos_ratio = event.position().x() / max(1, self.width())
        time_pos = pos_ratio * self._duration

        self.waveform_clicked.emit(time_pos)
        self._signals.waveform_position_selected.emit(time_pos)

    # ------------------------------------------------------------------
    # SIZE
    # ------------------------------------------------------------------

    def sizeHint(self) -> QSize:
        return QSize(400, 100)
