"""
NOSIS – Actions Panel
====================

Enterprise-grade contextual actions controller for Inspector Panel (2025–2026).

Purpose:
- Centralized command surface for track-level operations
- Context-aware, state-safe actions
- Bridge between Create workflow, Studio and backend pipelines
- Designed for high-frequency professional usage

ActionsPanel is NOT a toolbar.
It is a command orchestration layer.
"""

from __future__ import annotations

import logging
from typing import Optional, Dict

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QGroupBox,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.actions_panel")


class ActionsPanel(QFrame):
    """
    Context-aware actions panel for a selected track.

    Responsibilities:
    - Expose all high-level actions in one predictable place
    - Enable / disable actions based on track state
    - Emit structured intent events
    - Prevent destructive operations without context
    """

    action_requested = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()
        self._track_id: Optional[str] = None
        self._track_state: Dict = {}

        self.setObjectName("ActionsPanel")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self._init_ui()

        logger.info("ActionsPanel initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(10)

        # --------------------------------------------------------------
        # PRIMARY ACTIONS
        # --------------------------------------------------------------

        primary_group = QGroupBox("Primary Actions")
        primary_layout = QHBoxLayout(primary_group)

        self.play_btn = QPushButton("Play")
        self.open_studio_btn = QPushButton("Open in Studio")
        self.regenerate_btn = QPushButton("Regenerate")

        self.play_btn.clicked.connect(lambda: self._emit("play"))
        self.open_studio_btn.clicked.connect(lambda: self._emit("open_studio"))
        self.regenerate_btn.clicked.connect(lambda: self._emit("regenerate"))

        primary_layout.addWidget(self.play_btn)
        primary_layout.addWidget(self.open_studio_btn)
        primary_layout.addWidget(self.regenerate_btn)

        root.addWidget(primary_group)

        # --------------------------------------------------------------
        # SECONDARY ACTIONS
        # --------------------------------------------------------------

        secondary_group = QGroupBox("Secondary Actions")
        secondary_layout = QHBoxLayout(secondary_group)

        self.export_btn = QPushButton("Export")
        self.duplicate_btn = QPushButton("Duplicate")
        self.delete_btn = QPushButton("Delete")

        self.export_btn.clicked.connect(lambda: self._emit("export"))
        self.duplicate_btn.clicked.connect(lambda: self._emit("duplicate"))
        self.delete_btn.clicked.connect(lambda: self._emit("delete"))

        secondary_layout.addWidget(self.export_btn)
        secondary_layout.addWidget(self.duplicate_btn)
        secondary_layout.addWidget(self.delete_btn)

        root.addWidget(secondary_group)

        # --------------------------------------------------------------
        # AI ACTIONS
        # --------------------------------------------------------------

        ai_group = QGroupBox("AI Actions")
        ai_layout = QHBoxLayout(ai_group)

        self.regen_music_btn = QPushButton("Regenerate Music")
        self.regen_lyrics_btn = QPushButton("Regenerate Lyrics")
        self.regen_cover_btn = QPushButton("Regenerate Cover")

        self.regen_music_btn.clicked.connect(lambda: self._emit("regen_music"))
        self.regen_lyrics_btn.clicked.connect(lambda: self._emit("regen_lyrics"))
        self.regen_cover_btn.clicked.connect(lambda: self._emit("regen_cover"))

        ai_layout.addWidget(self.regen_music_btn)
        ai_layout.addWidget(self.regen_lyrics_btn)
        ai_layout.addWidget(self.regen_cover_btn)

        root.addWidget(ai_group)

        root.addStretch()
        self._set_enabled(False)

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def set_track(self, track_id: str, state: Optional[Dict] = None) -> None:
        self._track_id = track_id
        self._track_state = state or {}
        self._update_state()
        self._set_enabled(True)

    def clear(self) -> None:
        self._track_id = None
        self._track_state = {}
        self._set_enabled(False)

    # ------------------------------------------------------------------
    # INTERNAL
    # ------------------------------------------------------------------

    def _set_enabled(self, enabled: bool) -> None:
        for btn in [
            self.play_btn,
            self.open_studio_btn,
            self.regenerate_btn,
            self.export_btn,
            self.duplicate_btn,
            self.delete_btn,
            self.regen_music_btn,
            self.regen_lyrics_btn,
            self.regen_cover_btn,
        ]:
            btn.setEnabled(enabled)

    def _update_state(self) -> None:
        # Placeholder for future state-based logic
        pass

    def _emit(self, action: str) -> None:
        if not self._track_id:
            return

        payload = {
            "track_id": self._track_id,
            "action": action,
        }

        logger.debug("Action requested: %s", payload)

        self.action_requested.emit(payload)
        self._signals.track_action_requested.emit(payload)
