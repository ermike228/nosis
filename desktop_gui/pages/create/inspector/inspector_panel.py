"""
NOSIS – Inspector Panel
======================

Enterprise-grade Inspector Panel for Create workflow (2025–2026).

Purpose:
- Single source of truth for selected track state
- Deep inspection of metadata, AI history, quality and structure
- Fast context actions without switching screens
- Bridge between Library, Generator and Studio

InspectorPanel is NOT a details view.
It is an analytical command surface.
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
    QTextEdit,
    QGroupBox,
    QFormLayout,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.inspector")


class InspectorPanel(QFrame):
    """
    Inspector panel for currently selected track.

    Responsibilities:
    - Display canonical track metadata
    - Show AI generation & regeneration history
    - Expose quality signals and scores
    - Provide quick contextual actions
    """

    open_in_studio_requested = pyqtSignal(str)
    regenerate_requested = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()
        self._track: Optional[Dict] = None

        self.setObjectName("InspectorPanel")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumWidth(320)

        self._init_ui()
        self._bind_signals()

        logger.info("InspectorPanel initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(12)

        # --------------------------------------------------------------
        # HEADER
        # --------------------------------------------------------------

        self.title_label = QLabel("No track selected")
        self.title_label.setObjectName("InspectorTitle")
        self.title_label.setWordWrap(True)
        root.addWidget(self.title_label)

        # --------------------------------------------------------------
        # METADATA
        # --------------------------------------------------------------

        self.meta_group = QGroupBox("Metadata")
        meta_layout = QFormLayout(self.meta_group)

        self.style_label = QLabel("–")
        self.duration_label = QLabel("–")
        self.voice_label = QLabel("–")

        meta_layout.addRow("Style:", self.style_label)
        meta_layout.addRow("Duration:", self.duration_label)
        meta_layout.addRow("Voice:", self.voice_label)

        root.addWidget(self.meta_group)

        # --------------------------------------------------------------
        # PROMPTS
        # --------------------------------------------------------------

        self.prompt_group = QGroupBox("Generation Prompt")
        prompt_layout = QVBoxLayout(self.prompt_group)

        self.prompt_text = QTextEdit()
        self.prompt_text.setReadOnly(True)
        self.prompt_text.setPlaceholderText("Prompt used for generation")

        self.negative_prompt_text = QTextEdit()
        self.negative_prompt_text.setReadOnly(True)
        self.negative_prompt_text.setPlaceholderText("Negative prompt")

        prompt_layout.addWidget(QLabel("Prompt"))
        prompt_layout.addWidget(self.prompt_text)
        prompt_layout.addWidget(QLabel("Negative Prompt"))
        prompt_layout.addWidget(self.negative_prompt_text)

        root.addWidget(self.prompt_group)

        # --------------------------------------------------------------
        # AI HISTORY
        # --------------------------------------------------------------

        self.ai_group = QGroupBox("AI History")
        ai_layout = QVBoxLayout(self.ai_group)

        self.ai_history = QTextEdit()
        self.ai_history.setReadOnly(True)
        self.ai_history.setPlaceholderText("AI generation & regeneration history")

        ai_layout.addWidget(self.ai_history)
        root.addWidget(self.ai_group)

        # --------------------------------------------------------------
        # QUALITY
        # --------------------------------------------------------------

        self.quality_group = QGroupBox("Quality Analysis")
        quality_layout = QFormLayout(self.quality_group)

        self.quality_score = QLabel("–")
        self.originality_score = QLabel("–")

        quality_layout.addRow("Overall Quality:", self.quality_score)
        quality_layout.addRow("Originality:", self.originality_score)

        root.addWidget(self.quality_group)

        # --------------------------------------------------------------
        # ACTIONS
        # --------------------------------------------------------------

        actions = QHBoxLayout()

        self.regen_button = QPushButton("Regenerate")
        self.studio_button = QPushButton("Open in Studio")

        self.regen_button.clicked.connect(self._on_regenerate)
        self.studio_button.clicked.connect(self._on_open_studio)

        actions.addWidget(self.regen_button)
        actions.addWidget(self.studio_button)

        root.addLayout(actions)
        root.addStretch()

        self._set_enabled(False)

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _bind_signals(self) -> None:
        self._signals.track_selected.connect(self._on_track_selected)

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def set_track(self, track: Dict) -> None:
        self._track = track
        self._update_ui()
        self._set_enabled(True)

    def clear(self) -> None:
        self._track = None
        self.title_label.setText("No track selected")
        self._set_enabled(False)

    # ------------------------------------------------------------------
    # INTERNAL
    # ------------------------------------------------------------------

    def _update_ui(self) -> None:
        if not self._track:
            return

        self.title_label.setText(self._track.get("title", "Untitled"))
        self.style_label.setText(self._track.get("style", "–"))
        self.duration_label.setText(str(self._track.get("duration", "–")))
        self.voice_label.setText(self._track.get("voice", "–"))

        self.prompt_text.setText(self._track.get("prompt", ""))
        self.negative_prompt_text.setText(self._track.get("negative_prompt", ""))

        self.ai_history.setText(
            "\n".join(self._track.get("ai_history", []))
        )

        quality = self._track.get("quality", {})
        self.quality_score.setText(str(quality.get("overall", "–")))
        self.originality_score.setText(str(quality.get("originality", "–")))

    def _set_enabled(self, enabled: bool) -> None:
        self.meta_group.setEnabled(enabled)
        self.prompt_group.setEnabled(enabled)
        self.ai_group.setEnabled(enabled)
        self.quality_group.setEnabled(enabled)
        self.regen_button.setEnabled(enabled)
        self.studio_button.setEnabled(enabled)

    # ------------------------------------------------------------------
    # EVENTS
    # ------------------------------------------------------------------

    def _on_track_selected(self, track_id: str) -> None:
        # In real app, controller injects full track data
        logger.debug("Inspector received track selected: %s", track_id)

    def _on_regenerate(self) -> None:
        if not self._track:
            return
        track_id = self._track.get("id")
        self.regenerate_requested.emit(track_id)
        self._signals.regenerate_track_requested.emit(track_id)

    def _on_open_studio(self) -> None:
        if not self._track:
            return
        track_id = self._track.get("id")
        self.open_in_studio_requested.emit(track_id)
        self._signals.open_track_in_studio.emit(track_id)
