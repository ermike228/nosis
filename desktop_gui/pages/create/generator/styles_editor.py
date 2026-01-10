"""
NOSIS Desktop GUI – Styles Editor
================================

Enterprise-grade style, genre & mood design component (2025–2026).

Purpose:
- Deep musical style specification
- Genre & subgenre matrix (700+ scalable)
- Mood, energy, tempo & era descriptors
- Long-form style prompt (10k+ chars)
- Clean structured payload for AI generation

This is NOT a simple prompt field.
This is a musical style designer.
"""

from __future__ import annotations

import logging
from typing import Dict, List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QSlider,
    QSizePolicy,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.styles_editor")


# =============================================================================
# STYLES EDITOR
# =============================================================================

class StylesEditor(QFrame):
    """
    Advanced musical style editor.

    Combines:
    - Free-form style prompt
    - Structured musical descriptors
    - Genre & mood awareness
    """

    styles_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()

        self.setObjectName("StylesEditor")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._init_ui()

        logger.info("StylesEditor initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        # Header
        header = QHBoxLayout()
        title = QLabel("Style & Genre")
        title.setObjectName("StylesEditorTitle")

        header.addWidget(title)
        header.addStretch()
        root.addLayout(header)

        # ------------------------------------------------------------------
        # MAIN STYLE PROMPT
        # ------------------------------------------------------------------

        self.style_prompt = QTextEdit()
        self.style_prompt.setPlaceholderText(
            "Describe musical style, genre, influences, atmosphere.\n\n"
            "Example:\n"
            "Dark cinematic electronic track with slow tempo, "
            "deep analog synths, emotional progression, "
            "modern film score aesthetics, dystopian mood.\n\n"
            "(Up to 10,000 characters)"
        )
        self.style_prompt.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.style_prompt.textChanged.connect(self._emit_change)
        root.addWidget(self.style_prompt)

        # ------------------------------------------------------------------
        # STRUCTURED CONTROLS
        # ------------------------------------------------------------------

        structured = QHBoxLayout()
        structured.setSpacing(16)

        structured.addLayout(self._build_genre_block())
        structured.addLayout(self._build_mood_block())
        structured.addLayout(self._build_energy_block())

        root.addLayout(structured)

    # ------------------------------------------------------------------
    # GENRE
    # ------------------------------------------------------------------

    def _build_genre_block(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(6)

        label = QLabel("Genres")
        label.setObjectName("StylesBlockTitle")
        layout.addWidget(label)

        self.genre_list = QListWidget()
        self.genre_list.setSelectionMode(
            QListWidget.SelectionMode.MultiSelection
        )

        # Core genres (scales to 700+ dynamically later)
        for genre in [
            "Pop",
            "Electronic",
            "Hip-Hop",
            "Rock",
            "Jazz",
            "Classical",
            "Cinematic",
            "Ambient",
            "EDM",
            "Experimental",
        ]:
            item = QListWidgetItem(genre)
            self.genre_list.addItem(item)

        self.genre_list.itemSelectionChanged.connect(self._emit_change)
        layout.addWidget(self.genre_list)

        return layout

    # ------------------------------------------------------------------
    # MOOD
    # ------------------------------------------------------------------

    def _build_mood_block(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(6)

        label = QLabel("Mood")
        label.setObjectName("StylesBlockTitle")
        layout.addWidget(label)

        self.mood_selector = QComboBox()
        self.mood_selector.addItems(
            [
                "Neutral",
                "Happy",
                "Sad",
                "Dark",
                "Epic",
                "Calm",
                "Aggressive",
                "Romantic",
                "Hopeful",
                "Tense",
            ]
        )
        self.mood_selector.currentIndexChanged.connect(self._emit_change)

        layout.addWidget(self.mood_selector)

        return layout

    # ------------------------------------------------------------------
    # ENERGY / TEMPO
    # ------------------------------------------------------------------

    def _build_energy_block(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(6)

        label = QLabel("Energy / Tempo")
        label.setObjectName("StylesBlockTitle")
        layout.addWidget(label)

        self.energy_slider = LabeledSlider("Energy")
        self.tempo_slider = LabeledSlider("Tempo")

        self.energy_slider.valueChanged.connect(self._emit_change)
        self.tempo_slider.valueChanged.connect(self._emit_change)

        layout.addWidget(self.energy_slider)
        layout.addWidget(self.tempo_slider)

        return layout

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def get_payload(self) -> Dict[str, object]:
        """
        Structured style payload for generation.
        """
        return {
            "prompt": self.style_prompt.toPlainText(),
            "genres": [
                item.text()
                for item in self.genre_list.selectedItems()
            ],
            "mood": self.mood_selector.currentText(),
            "energy": self.energy_slider.value(),
            "tempo": self.tempo_slider.value(),
        }

    def clear(self) -> None:
        self.style_prompt.clear()
        self.genre_list.clearSelection()

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _emit_change(self) -> None:
        payload = self.get_payload()
        self.styles_changed.emit(payload)
        self._signals.styles_updated.emit(payload)


# =============================================================================
# COMPONENTS
# =============================================================================

class LabeledSlider(QFrame):
    """
    Slider with label and numeric value.
    """

    valueChanged = pyqtSignal(int)

    def __init__(self, label: str):
        super().__init__()

        self._label_text = label

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.label = QLabel(f"{label}: 50")
        self.label.setObjectName("StylesSliderLabel")
        layout.addWidget(self.label)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self._on_change)

        layout.addWidget(self.slider)

    def _on_change(self, value: int):
        self.label.setText(f"{self._label_text}: {value}")
        self.valueChanged.emit(value)

    def value(self) -> int:
        return self.slider.value()
