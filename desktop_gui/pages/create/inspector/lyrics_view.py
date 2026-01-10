"""
NOSIS – Lyrics View
==================

Enterprise-grade lyrics inspection and control module for Inspector Panel (2025–2026).

Purpose:
- Canonical visualization of generated lyrics
- Safe editing with AI-awareness
- Support for multi-language, timing and semantic annotations
- Bridge between Generator, Inspector and Studio vocal timeline

LyricsView is NOT a text editor.
It is a semantic lyric surface.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional, List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QCheckBox,
    QGroupBox,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.lyrics_view")


class LyricsView(QFrame):
    """
    Lyrics visualization and controlled editing panel.

    Responsibilities:
    - Display lyrics with structure (verses / chorus / bridge)
    - Allow safe edits without breaking AI reproducibility
    - Provide semantic actions (lock, regenerate, analyze)
    - Act as lyric authority in UI layer
    """

    lyrics_changed = pyqtSignal(dict)
    regenerate_requested = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()
        self._track_id: Optional[str] = None
        self._lyrics: str = ""
        self._language: str = "unknown"

        self.setObjectName("LyricsView")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._init_ui()

        logger.info("LyricsView initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(10)

        # --------------------------------------------------------------
        # HEADER
        # --------------------------------------------------------------

        header = QHBoxLayout()

        self.language_label = QLabel("Language: –")
        self.lock_checkbox = QCheckBox("Lock lyrics (semantic)")

        self.lock_checkbox.stateChanged.connect(self._on_lock_changed)

        header.addWidget(self.language_label)
        header.addStretch()
        header.addWidget(self.lock_checkbox)

        root.addLayout(header)

        # --------------------------------------------------------------
        # LYRICS TEXT
        # --------------------------------------------------------------

        self.lyrics_edit = QTextEdit()
        self.lyrics_edit.setPlaceholderText(
            "Lyrics will appear here.\n\n"
            "Verses, choruses and bridges are preserved semantically."
        )

        self.lyrics_edit.textChanged.connect(self._on_text_changed)
        root.addWidget(self.lyrics_edit)

        # --------------------------------------------------------------
        # ACTIONS
        # --------------------------------------------------------------

        actions = QHBoxLayout()

        self.regenerate_btn = QPushButton("Regenerate lyrics")
        self.analyze_btn = QPushButton("Analyze lyrics")

        self.regenerate_btn.clicked.connect(self._on_regenerate)
        self.analyze_btn.clicked.connect(self._on_analyze)

        actions.addWidget(self.regenerate_btn)
        actions.addWidget(self.analyze_btn)

        root.addLayout(actions)

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def set_lyrics(self, track_id: str, lyrics: str, language: str = "unknown") -> None:
        self._track_id = track_id
        self._lyrics = lyrics or ""
        self._language = language

        self.language_label.setText(f"Language: {language}")
        self.lyrics_edit.blockSignals(True)
        self.lyrics_edit.setText(self._lyrics)
        self.lyrics_edit.blockSignals(False)

    def clear(self) -> None:
        self._track_id = None
        self._lyrics = ""
        self._language = "unknown"
        self.language_label.setText("Language: –")
        self.lyrics_edit.clear()

    # ------------------------------------------------------------------
    # INTERNAL
    # ------------------------------------------------------------------

    def _on_text_changed(self) -> None:
        if not self._track_id:
            return

        self._lyrics = self.lyrics_edit.toPlainText()

        payload = {
            "track_id": self._track_id,
            "lyrics": self._lyrics,
        }

        self.lyrics_changed.emit(payload)
        self._signals.lyrics_updated.emit(payload)

    def _on_lock_changed(self, state: int) -> None:
        if not self._track_id:
            return

        locked = state == Qt.CheckState.Checked
        self._signals.lyrics_lock_toggled.emit({
            "track_id": self._track_id,
            "locked": locked,
        })

    def _on_regenerate(self) -> None:
        if not self._track_id:
            return

        self.regenerate_requested.emit(self._track_id)
        self._signals.regenerate_lyrics_requested.emit(self._track_id)

    def _on_analyze(self) -> None:
        if not self._track_id:
            return

        self._signals.analyze_lyrics_requested.emit({
            "track_id": self._track_id,
            "lyrics": self._lyrics,
            "language": self._language,
        })
