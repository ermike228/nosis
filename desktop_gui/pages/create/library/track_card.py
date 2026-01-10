"""
NOSIS – Track Card
=================

Enterprise-grade visual representation of a generated track (2025–2026).

Purpose:
- Canonical UI unit for representing a single track in Library
- Bridge between generation, inspection and Studio
- High-density information without visual overload
- Designed for thousands of tracks and long sessions

TrackCard is NOT just a widget.
It is a semantic object in the UI layer.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.track_card")


class TrackCard(QFrame):
    """
    Visual + semantic representation of a generated track.

    Responsibilities:
    - Display essential metadata
    - Provide fast actions (play, open, regenerate)
    - Act as selection surface
    - Emit structured events, not logic
    """

    selected = pyqtSignal(str)
    play_requested = pyqtSignal(str)
    open_in_studio_requested = pyqtSignal(str)
    regenerate_requested = pyqtSignal(str)

    def __init__(self, track: Dict):
        super().__init__()

        self._signals = get_signals()
        self._track = track

        self.setObjectName("TrackCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._init_ui()
        self._bind_signals()

        logger.debug("TrackCard created for track %s", track.get("id"))

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(6)

        # --------------------------------------------------------------
        # TITLE
        # --------------------------------------------------------------

        self.title_label = QLabel(self._track.get("title", "Untitled"))
        self.title_label.setObjectName("TrackTitle")
        self.title_label.setWordWrap(True)

        root.addWidget(self.title_label)

        # --------------------------------------------------------------
        # META
        # --------------------------------------------------------------

        meta_row = QHBoxLayout()

        self.style_label = QLabel(self._track.get("style", ""))
        self.style_label.setObjectName("TrackStyle")

        duration = self._track.get("duration", 0)
        self.duration_label = QLabel(self._format_duration(duration))

        meta_row.addWidget(self.style_label)
        meta_row.addStretch()
        meta_row.addWidget(self.duration_label)

        root.addLayout(meta_row)

        # --------------------------------------------------------------
        # BADGES
        # --------------------------------------------------------------

        badges_row = QHBoxLayout()

        if self._track.get("has_vocals"):
            badges_row.addWidget(QLabel("Vocals"))

        if self._track.get("ai_regenerated"):
            badges_row.addWidget(QLabel("AI Edited"))

        root.addLayout(badges_row)

        # --------------------------------------------------------------
        # ACTIONS
        # --------------------------------------------------------------

        actions = QHBoxLayout()

        self.play_button = QPushButton("Play")
        self.open_button = QPushButton("Studio")
        self.regen_button = QPushButton("Regenerate")

        self.play_button.clicked.connect(self._on_play)
        self.open_button.clicked.connect(self._on_open)
        self.regen_button.clicked.connect(self._on_regenerate)

        actions.addWidget(self.play_button)
        actions.addWidget(self.open_button)
        actions.addWidget(self.regen_button)

        root.addLayout(actions)

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _bind_signals(self) -> None:
        pass

    # ------------------------------------------------------------------
    # EVENTS
    # ------------------------------------------------------------------

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected.emit(self._track.get("id"))
            self._signals.track_selected.emit(self._track.get("id"))

    def _on_play(self) -> None:
        self.play_requested.emit(self._track.get("id"))
        self._signals.play_track_requested.emit(self._track.get("id"))

    def _on_open(self) -> None:
        self.open_in_studio_requested.emit(self._track.get("id"))
        self._signals.open_track_in_studio.emit(self._track.get("id"))

    def _on_regenerate(self) -> None:
        self.regenerate_requested.emit(self._track.get("id"))
        self._signals.regenerate_track_requested.emit(self._track.get("id"))

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _format_duration(seconds: int) -> str:
        minutes = seconds // 60
        sec = seconds % 60
        return f"{minutes}:{sec:02d}"
