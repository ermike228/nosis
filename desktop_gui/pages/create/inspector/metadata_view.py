"""
NOSIS – Metadata View
====================

Enterprise-grade metadata visualization and control module for Inspector Panel (2025–2026).

Purpose:
- Canonical representation of all semantic, musical and technical metadata
- Editable + read-only hybrid view (enterprise-safe)
- Backbone for search, filtering, analytics and Studio handoff
- Single source of metadata truth in UI layer

MetadataView is NOT a form.
It is a semantic projection of a track.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QGroupBox,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.metadata_view")


class MetadataView(QFrame):
    """
    Metadata visualization and editing surface.

    Responsibilities:
    - Display full metadata set of selected track
    - Allow safe edits to non-destructive fields
    - Act as metadata authority for UI
    - Emit structured metadata updates
    """

    metadata_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()
        self._track_id: Optional[str] = None
        self._metadata: Dict = {}

        self.setObjectName("MetadataView")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._init_ui()

        logger.info("MetadataView initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(10)

        # --------------------------------------------------------------
        # BASIC
        # --------------------------------------------------------------

        self.basic_group = QGroupBox("Basic Metadata")
        basic_layout = QFormLayout(self.basic_group)

        self.title_input = QLineEdit()
        self.artist_input = QLineEdit()
        self.genre_input = QComboBox()
        self.genre_input.addItems([
            "Unknown", "Pop", "Electronic", "Hip-Hop", "Cinematic",
            "Ambient", "Rock", "Experimental"
        ])

        basic_layout.addRow("Title", self.title_input)
        basic_layout.addRow("Artist", self.artist_input)
        basic_layout.addRow("Genre", self.genre_input)

        root.addWidget(self.basic_group)

        # --------------------------------------------------------------
        # TECHNICAL
        # --------------------------------------------------------------

        self.tech_group = QGroupBox("Technical Metadata")
        tech_layout = QFormLayout(self.tech_group)

        self.duration_label = QLabel("–")
        self.bpm_label = QLabel("–")
        self.key_label = QLabel("–")

        tech_layout.addRow("Duration", self.duration_label)
        tech_layout.addRow("BPM", self.bpm_label)
        tech_layout.addRow("Key", self.key_label)

        root.addWidget(self.tech_group)

        # --------------------------------------------------------------
        # AI
        # --------------------------------------------------------------

        self.ai_group = QGroupBox("AI Metadata")
        ai_layout = QFormLayout(self.ai_group)

        self.model_label = QLabel("–")
        self.seed_label = QLabel("–")
        self.quality_label = QLabel("–" )

        ai_layout.addRow("Model", self.model_label)
        ai_layout.addRow("Seed", self.seed_label)
        ai_layout.addRow("Quality", self.quality_label)

        root.addWidget(self.ai_group)

        # --------------------------------------------------------------
        # TAGS
        # --------------------------------------------------------------

        self.tags_group = QGroupBox("Tags & Notes")
        tags_layout = QVBoxLayout(self.tags_group)

        self.tags_input = QTextEdit()
        self.tags_input.setPlaceholderText("Comma separated tags" )

        tags_layout.addWidget(self.tags_input)

        root.addWidget(self.tags_group)

        root.addStretch()

        # Bind edits
        self.title_input.editingFinished.connect(self._emit_update)
        self.artist_input.editingFinished.connect(self._emit_update)
        self.genre_input.currentIndexChanged.connect(self._emit_update)
        self.tags_input.textChanged.connect(self._emit_update)

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def set_metadata(self, track_id: str, metadata: Dict) -> None:
        self._track_id = track_id
        self._metadata = dict(metadata)

        self.title_input.setText(metadata.get("title", ""))
        self.artist_input.setText(metadata.get("artist", ""))

        genre = metadata.get("genre", "Unknown")
        if genre in [self.genre_input.itemText(i) for i in range(self.genre_input.count())]:
            self.genre_input.setCurrentText(genre)

        self.duration_label.setText(str(metadata.get("duration", "–")))
        self.bpm_label.setText(str(metadata.get("bpm", "–")))
        self.key_label.setText(str(metadata.get("key", "–")))

        self.model_label.setText(metadata.get("model", "–"))
        self.seed_label.setText(str(metadata.get("seed", "–")))
        self.quality_label.setText(str(metadata.get("quality", "–")))

        self.tags_input.setText(", ".join(metadata.get("tags", [])))

    # ------------------------------------------------------------------
    # INTERNAL
    # ------------------------------------------------------------------

    def _emit_update(self) -> None:
        if not self._track_id:
            return

        payload = {
            "track_id": self._track_id,
            "title": self.title_input.text(),
            "artist": self.artist_input.text(),
            "genre": self.genre_input.currentText(),
            "tags": [t.strip() for t in self.tags_input.toPlainText().split(",") if t.strip()],
        }

        self.metadata_changed.emit(payload)
        self._signals.metadata_updated.emit(payload)
