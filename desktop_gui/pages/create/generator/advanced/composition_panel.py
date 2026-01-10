"""
NOSIS – Advanced Composition Panel
=================================

Enterprise-grade composition & musical structure control system (2025–2026).

Purpose:
- Control musical form and macro-structure
- Phrase, section & progression logic
- Human-like composition reasoning
- Semantic-ready composition graph
- Foundation for "thinking composer" behavior

This module defines HOW the music is BUILT over time.
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
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QSlider,
    QCheckBox,
    QSizePolicy,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.composition_panel")


# =============================================================================
# COMPOSITION PANEL
# =============================================================================

class CompositionPanel(QFrame):
    """
    Advanced composition configuration panel.

    Controls:
    - Song form & structure
    - Section balance & development
    - Harmonic & melodic motion
    - Repetition vs evolution
    - Composer-like reasoning hints
    """

    composition_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()

        self.setObjectName("CompositionPanel")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._init_ui()

        logger.info("CompositionPanel initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        # --------------------------------------------------------------
        # GLOBAL FORM
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Musical Form"))

        self.form = QComboBox()
        self.form.addItems([
            "Auto (AI decides)",
            "Verse – Chorus",
            "Verse – Chorus – Bridge",
            "AABA",
            "Through-composed",
            "Minimal / Loop-based",
            "Cinematic Arc",
            "Experimental / Free",
        ])
        self.form.currentIndexChanged.connect(self._emit_change)
        root.addWidget(self.form)

        # --------------------------------------------------------------
        # SECTION BALANCE
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Section Balance"))

        self.verse_weight = LabeledSlider(
            "Verse Presence",
            "How dominant verses are in the composition",
            default=50,
        )
        self.chorus_weight = LabeledSlider(
            "Chorus Impact",
            "How strong and memorable the chorus is",
            default=65,
        )
        self.bridge_weight = LabeledSlider(
            "Bridge Contrast",
            "Degree of contrast introduced by bridges",
            default=40,
        )

        for s in (self.verse_weight, self.chorus_weight, self.bridge_weight):
            s.valueChanged.connect(self._emit_change)
            root.addWidget(s)

        # --------------------------------------------------------------
        # DEVELOPMENT & EVOLUTION
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Development & Evolution"))

        self.progression_complexity = LabeledSlider(
            "Harmonic Complexity",
            "Chord richness and progression sophistication",
            default=55,
        )
        self.melodic_variation = LabeledSlider(
            "Melodic Evolution",
            "How melodies change over time",
            default=60,
        )
        self.arrangement_growth = LabeledSlider(
            "Arrangement Growth",
            "How layers and instruments evolve",
            default=70,
        )

        for s in (
            self.progression_complexity,
            self.melodic_variation,
            self.arrangement_growth,
        ):
            s.valueChanged.connect(self._emit_change)
            root.addWidget(s)

        # --------------------------------------------------------------
        # REPETITION VS NOVELTY
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Repetition vs Novelty"))

        self.repetition = LabeledSlider(
            "Motif Repetition",
            "Reuse of musical ideas and motifs",
            default=50,
        )
        self.surprise = LabeledSlider(
            "Surprise Factor",
            "Unexpected changes and variations",
            default=35,
        )

        self.repetition.valueChanged.connect(self._emit_change)
        self.surprise.valueChanged.connect(self._emit_change)

        root.addWidget(self.repetition)
        root.addWidget(self.surprise)

        # --------------------------------------------------------------
        # COMPOSER REASONING
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Composer Reasoning"))

        self.goal_directed = QCheckBox(
            "Goal-oriented composition (build toward climax)"
        )
        self.goal_directed.setChecked(True)
        self.goal_directed.stateChanged.connect(self._emit_change)

        self.thematic_consistency = QCheckBox(
            "Maintain thematic consistency"
        )
        self.thematic_consistency.setChecked(True)
        self.thematic_consistency.stateChanged.connect(self._emit_change)

        self.emotional_arc = QCheckBox(
            "Emotional arc over time"
        )
        self.emotional_arc.setChecked(True)
        self.emotional_arc.stateChanged.connect(self._emit_change)

        root.addWidget(self.goal_directed)
        root.addWidget(self.thematic_consistency)
        root.addWidget(self.emotional_arc)

        root.addStretch()

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def get_payload(self) -> Dict[str, object]:
        """
        Structured composition payload.

        This payload feeds the semantic engine and generation backend.
        """
        return {
            "form": self.form.currentText(),
            "sections": {
                "verse_weight": self.verse_weight.value(),
                "chorus_weight": self.chorus_weight.value(),
                "bridge_weight": self.bridge_weight.value(),
            },
            "development": {
                "harmonic_complexity": self.progression_complexity.value(),
                "melodic_variation": self.melodic_variation.value(),
                "arrangement_growth": self.arrangement_growth.value(),
            },
            "structure_dynamics": {
                "repetition": self.repetition.value(),
                "surprise": self.surprise.value(),
            },
            "composer_reasoning": {
                "goal_directed": self.goal_directed.isChecked(),
                "thematic_consistency": self.thematic_consistency.isChecked(),
                "emotional_arc": self.emotional_arc.isChecked(),
            },
        }

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _emit_change(self) -> None:
        payload = self.get_payload()
        self.composition_changed.emit(payload)
        self._signals.composition_config_updated.emit(payload)


# =============================================================================
# COMPONENTS
# =============================================================================

class SectionLabel(QLabel):
    def __init__(self, text: str):
        super().__init__(text)
        self.setObjectName("CompositionSectionLabel")


class LabeledSlider(QFrame):
    """
    Slider with musical semantics and feedback.
    """

    valueChanged = pyqtSignal(int)

    def __init__(
        self,
        title: str,
        description: str,
        *,
        default: int = 50,
    ):
        super().__init__()

        self._title = title

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.label = QLabel(f"{title}: {default}")
        self.label.setObjectName("CompositionSliderTitle")
        layout.addWidget(self.label)

        desc = QLabel(description)
        desc.setObjectName("CompositionSliderDescription")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(default)
        self.slider.valueChanged.connect(self._on_change)

        layout.addWidget(self.slider)

    def _on_change(self, value: int):
        self.label.setText(f"{self._title}: {value}")
        self.valueChanged.emit(value)

    def value(self) -> int:
        return self.slider.value()
