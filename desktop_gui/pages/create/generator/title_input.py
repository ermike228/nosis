"""
NOSIS – Title Input Panel
========================

Enterprise-grade title management & semantic naming system (2025–2026).

Purpose:
- Explicit control over track naming
- Semantic guidance for generation & ranking
- Professional project organization
- Metadata integrity across pipeline

This module defines HOW a track is NAMED and IDENTIFIED.
"""

from __future__ import annotations

import logging
from typing import Dict

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.title_input")


class TitleInput(QFrame):
    """
    Advanced title & naming control.

    Covers:
    - Manual title input
    - AI-assisted title generation toggle
    - Semantic weighting of title
    - Metadata propagation
    """

    title_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()

        self.setObjectName("TitleInput")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._init_ui()

        logger.info("TitleInput initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        root.addWidget(QLabel("Track Title"))

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText(
            "Enter track title (optional but recommended)"
        )
        self.title_edit.textChanged.connect(self._emit_change)
        root.addWidget(self.title_edit)

        self.ai_assist = QCheckBox(
            "Allow AI to refine or suggest title"
        )
        self.ai_assist.setChecked(True)
        self.ai_assist.stateChanged.connect(self._emit_change)
        root.addWidget(self.ai_assist)

        self.semantic_weight = QCheckBox(
            "Use title as semantic guidance for generation"
        )
        self.semantic_weight.setChecked(True)
        self.semantic_weight.stateChanged.connect(self._emit_change)
        root.addWidget(self.semantic_weight)

        root.addStretch()

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def get_payload(self) -> Dict[str, object]:
        """
        Structured title payload.
        """
        return {
            "title": self.title_edit.text().strip(),
            "ai_assist": self.ai_assist.isChecked(),
            "semantic_weight": self.semantic_weight.isChecked(),
        }

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _emit_change(self) -> None:
        payload = self.get_payload()
        self.title_changed.emit(payload)
        self._signals.title_updated.emit(payload)
