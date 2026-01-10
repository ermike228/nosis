"""
NOSIS Desktop GUI – Lyrics Editor
================================

Enterprise-grade lyrics authoring & analysis component (2025–2026).

Purpose:
- Professional lyric writing environment
- Structural awareness (verses, chorus, bridge)
- Future-ready timing & vocal alignment
- Emotion & delivery hints
- Clean payload export for generation pipeline

This is NOT a simple text box.
This is a lyric composition tool.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QComboBox,
    QSizePolicy,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.lyrics_editor")


# =============================================================================
# LYRICS EDITOR
# =============================================================================

class LyricsEditor(QFrame):
    """
    Advanced lyrics editor with structural semantics.

    Features:
    - Section-based writing
    - Inline structure markers
    - Emotion / delivery hints
    - Clean export to generation payload
    """

    lyrics_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()

        self.setObjectName("LyricsEditor")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._current_structure: str = "free"

        self._init_ui()

        logger.info("LyricsEditor initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        # Header
        header = QHBoxLayout()
        title = QLabel("Lyrics")
        title.setObjectName("LyricsEditorTitle")

        self.structure_selector = QComboBox()
        self.structure_selector.addItems(
            [
                "Free form",
                "Verse / Chorus",
                "Verse / Chorus / Bridge",
                "Storytelling",
                "Rap / Bars",
            ]
        )
        self.structure_selector.currentIndexChanged.connect(
            self._on_structure_changed
        )

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.structure_selector)
        root.addLayout(header)

        # Editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText(
            "Write lyrics here…\n\n"
            "[Verse]\n...\n\n"
            "[Chorus]\n..."
        )
        self.editor.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.editor.textChanged.connect(self._emit_change)

        root.addWidget(self.editor)

        # Footer tools
        tools = QHBoxLayout()

        self.emotion_selector = QComboBox()
        self.emotion_selector.addItems(
            [
                "Neutral",
                "Sad",
                "Happy",
                "Aggressive",
                "Intimate",
                "Epic",
                "Dark",
                "Hopeful",
            ]
        )
        self.emotion_selector.currentIndexChanged.connect(self._emit_change)

        self.delivery_selector = QComboBox()
        self.delivery_selector.addItems(
            [
                "Natural",
                "Soft",
                "Powerful",
                "Whispered",
                "Shouted",
                "Melodic",
                "Spoken",
            ]
        )
        self.delivery_selector.currentIndexChanged.connect(self._emit_change)

        tools.addWidget(QLabel("Emotion"))
        tools.addWidget(self.emotion_selector)
        tools.addSpacing(12)
        tools.addWidget(QLabel("Delivery"))
        tools.addWidget(self.delivery_selector)
        tools.addStretch()

        root.addLayout(tools)

    # ------------------------------------------------------------------
    # STRUCTURE
    # ------------------------------------------------------------------

    def _on_structure_changed(self, index: int) -> None:
        self._current_structure = self.structure_selector.currentText()
        self._emit_change()

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def get_payload(self) -> Dict[str, object]:
        """
        Export lyrics data for generation.

        This structure is stable and versionable.
        """
        return {
            "text": self.editor.toPlainText(),
            "structure": self._current_structure,
            "emotion": self.emotion_selector.currentText(),
            "delivery": self.delivery_selector.currentText(),
        }

    def set_lyrics(self, text: str) -> None:
        self.editor.setPlainText(text)

    def clear(self) -> None:
        self.editor.clear()

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _emit_change(self) -> None:
        payload = self.get_payload()
        self.lyrics_changed.emit(payload)
        self._signals.lyrics_updated.emit(payload)
