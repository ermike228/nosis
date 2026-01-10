"""
NOSIS – Negative Prompt Panel
=============================

Enterprise-grade negative constraint & rejection system (2025–2026).

Purpose:
- Explicitly define what MUST NOT appear in generation
- Reduce neural artifacts, clichés and unwanted patterns
- Act as a semantic rejection layer before & after generation
- Increase controllability, safety and professional quality

This module defines WHAT the AI must actively AVOID.
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
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QCheckBox,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.negative_prompt")


class NegativePromptPanel(QFrame):
    """
    Advanced negative prompt & rejection control panel.

    Covers:
    - Textual negative prompt
    - Structured rejection categories
    - AI artifact suppression
    - Genre & vocal exclusions
    - Semantic hard constraints
    """

    negative_prompt_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()

        self.setObjectName("NegativePromptPanel")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._init_ui()

        logger.info("NegativePromptPanel initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        # --------------------------------------------------------------
        # FREEFORM NEGATIVE PROMPT
        # --------------------------------------------------------------

        root.addWidget(QLabel("Negative Prompt (Freeform)"))

        self.text_prompt = QTextEdit()
        self.text_prompt.setPlaceholderText(
            "Describe what the AI should avoid."
            "Examples:"
            "- robotic vocals"
            "- cheesy melodies"
            "- lo-fi artifacts"
            "- overcompressed sound"
            "- generic pop clichés"
        )
        self.text_prompt.textChanged.connect(self._emit_change)
        root.addWidget(self.text_prompt)

        # --------------------------------------------------------------
        # STRUCTURED EXCLUSIONS
        # --------------------------------------------------------------

        root.addWidget(QLabel("Structured Exclusions"))

        self.exclusion_list = QListWidget()
        self.exclusion_list.setSelectionMode(
            QListWidget.SelectionMode.MultiSelection
        )

        exclusions = [
            "Robotic / synthetic vocal tone",
            "Monotone delivery",
            "Over-autotune",
            "AI artifacts / glitches",
            "Harsh sibilance",
            "Excessive compression",
            "Flat dynamics",
            "Generic chord progressions",
            "Predictable melodies",
            "Unwanted genre tropes",
            "Cliché lyrics",
            "Poor pronunciation",
            "Timing jitter",
            "Phase issues",
            "Muddy low end",
            "Shrill highs",
        ]

        for item in exclusions:
            QListWidgetItem(item, self.exclusion_list)

        self.exclusion_list.itemSelectionChanged.connect(self._emit_change)
        root.addWidget(self.exclusion_list)

        # --------------------------------------------------------------
        # AI FAILURE MODES
        # --------------------------------------------------------------

        root.addWidget(QLabel("AI Failure Mode Suppression"))

        self.reject_repetition = QCheckBox(
            "Reject repetitive or looping outputs"
        )
        self.reject_repetition.setChecked(True)
        self.reject_repetition.stateChanged.connect(self._emit_change)

        self.reject_low_quality = QCheckBox(
            "Reject low-quality generations automatically"
        )
        self.reject_low_quality.setChecked(True)
        self.reject_low_quality.stateChanged.connect(self._emit_change)

        self.reject_incoherent = QCheckBox(
            "Reject incoherent structure or form"
        )
        self.reject_incoherent.setChecked(True)
        self.reject_incoherent.stateChanged.connect(self._emit_change)

        root.addWidget(self.reject_repetition)
        root.addWidget(self.reject_low_quality)
        root.addWidget(self.reject_incoherent)

        # --------------------------------------------------------------
        # HARD SAFETY CONSTRAINTS
        # --------------------------------------------------------------

        root.addWidget(QLabel("Hard Safety Constraints"))

        self.no_copyright = QCheckBox(
            "Avoid melodies too similar to known songs"
        )
        self.no_copyright.setChecked(True)
        self.no_copyright.stateChanged.connect(self._emit_change)

        self.no_offensive = QCheckBox(
            "Avoid offensive or unsafe content"
        )
        self.no_offensive.setChecked(True)
        self.no_offensive.stateChanged.connect(self._emit_change)

        root.addWidget(self.no_copyright)
        root.addWidget(self.no_offensive)

        root.addStretch()

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def get_payload(self) -> Dict[str, object]:
        """
        Structured negative prompt payload.
        """
        return {
            "text_negative_prompt": self.text_prompt.toPlainText(),
            "structured_exclusions": [
                item.text()
                for item in self.exclusion_list.selectedItems()
            ],
            "ai_failure_rejection": {
                "reject_repetition": self.reject_repetition.isChecked(),
                "reject_low_quality": self.reject_low_quality.isChecked(),
                "reject_incoherent": self.reject_incoherent.isChecked(),
            },
            "safety": {
                "avoid_copyright_similarity": self.no_copyright.isChecked(),
                "avoid_offensive_content": self.no_offensive.isChecked(),
            },
        }

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _emit_change(self) -> None:
        payload = self.get_payload()
        self.negative_prompt_changed.emit(payload)
        self._signals.negative_prompt_updated.emit(payload)
