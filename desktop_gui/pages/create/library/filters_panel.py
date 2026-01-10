"""
NOSIS – Library Filters Panel
=============================

Enterprise-grade multi-dimensional filtering system for generated assets (2025–2026).

Purpose:
- Precise filtering of large music libraries
- Combination of technical, musical and AI-related attributes
- Scalable to thousands of tracks and future metadata
- Acts as a control surface, not a data processor

This module defines HOW users NARROW DOWN results in professional workflows.
"""

from __future__ import annotations

import logging
from typing import Dict

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QCheckBox,
    QSlider,
    QPushButton,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.filters_panel")


class LibraryFiltersPanel(QFrame):
    """
    Advanced filters panel for LibraryPanel.
    """

    filters_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._signals = get_signals()

        self.setObjectName("LibraryFiltersPanel")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._init_ui()
        logger.info("LibraryFiltersPanel initialized")

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        root.addWidget(QLabel("Genre"))
        self.genre_filter = QComboBox()
        self.genre_filter.addItems([
            "Any", "Pop", "Electronic", "Hip-Hop", "Cinematic",
            "Ambient", "Rock", "Experimental"
        ])
        self.genre_filter.currentIndexChanged.connect(self._emit_change)
        root.addWidget(self.genre_filter)

        root.addWidget(QLabel("Vocals"))
        self.with_vocals = QCheckBox("With vocals")
        self.instrumental = QCheckBox("Instrumental")
        self.with_vocals.stateChanged.connect(self._emit_change)
        self.instrumental.stateChanged.connect(self._emit_change)
        root.addWidget(self.with_vocals)
        root.addWidget(self.instrumental)

        root.addWidget(QLabel("Minimum Quality"))
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(0, 100)
        self.quality_slider.setValue(60)
        self.quality_slider.valueChanged.connect(self._emit_change)
        root.addWidget(self.quality_slider)

        root.addWidget(QLabel("AI Properties"))
        self.ai_generated = QCheckBox("AI generated")
        self.ai_edited = QCheckBox("Edited in Studio")
        self.ai_regenerated = QCheckBox("Has regenerated parts")
        self.ai_generated.stateChanged.connect(self._emit_change)
        self.ai_edited.stateChanged.connect(self._emit_change)
        self.ai_regenerated.stateChanged.connect(self._emit_change)
        root.addWidget(self.ai_generated)
        root.addWidget(self.ai_edited)
        root.addWidget(self.ai_regenerated)

        root.addWidget(QLabel("Creation Time"))
        self.time_filter = QComboBox()
        self.time_filter.addItems([
            "Any time", "Today", "Last 7 days", "Last 30 days", "Older"
        ])
        self.time_filter.currentIndexChanged.connect(self._emit_change)
        root.addWidget(self.time_filter)

        reset_button = QPushButton("Reset filters")
        reset_button.clicked.connect(self._reset_filters)
        root.addWidget(reset_button)

        root.addStretch()

    def get_payload(self) -> Dict[str, object]:
        return {
            "genre": self.genre_filter.currentText(),
            "vocals": {
                "with_vocals": self.with_vocals.isChecked(),
                "instrumental": self.instrumental.isChecked(),
            },
            "quality_min": self.quality_slider.value(),
            "ai": {
                "generated": self.ai_generated.isChecked(),
                "edited": self.ai_edited.isChecked(),
                "regenerated": self.ai_regenerated.isChecked(),
            },
            "created_at": self.time_filter.currentText(),
        }

    def _emit_change(self) -> None:
        payload = self.get_payload()
        self.filters_changed.emit(payload)
        self._signals.library_filters_updated.emit(payload)

    def _reset_filters(self) -> None:
        self.genre_filter.setCurrentIndex(0)
        self.with_vocals.setChecked(False)
        self.instrumental.setChecked(False)
        self.quality_slider.setValue(60)
        self.ai_generated.setChecked(False)
        self.ai_edited.setChecked(False)
        self.ai_regenerated.setChecked(False)
        self.time_filter.setCurrentIndex(0)
        self._emit_change()
