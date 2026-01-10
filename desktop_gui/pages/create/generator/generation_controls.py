"""
NOSIS Desktop GUI – Generation Controls
======================================

Enterprise-grade generation control panel (2025–2026).

Purpose:
- Fine-grained control over AI generation behavior
- Bridge between human intent and model parameters
- Unified control layer for music, vocal & arrangement generation

This module defines HOW the AI should think, not WHAT it should generate.
"""

from __future__ import annotations

import logging
from typing import Dict

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QComboBox,
    QCheckBox,
    QSizePolicy,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.generation_controls")


# =============================================================================
# GENERATION CONTROLS
# =============================================================================

class GenerationControls(QFrame):
    """
    Advanced generation behavior controls.

    Controls exposed here:
    - Prompt adherence
    - Reference influence
    - Creativity / divergence
    - Generation mode
    - Mastering & post-processing flags
    """

    controls_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()

        self.setObjectName("GenerationControls")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._init_ui()

        logger.info("GenerationControls initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        # --------------------------------------------------------------
        # MODE
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Generation Mode"))

        self.mode_selector = QComboBox()
        self.mode_selector.addItems(
            [
                "Song (with vocals)",
                "Instrumental",
                "Vocal stems only",
                "Backing track",
                "Experimental / abstract",
            ]
        )
        self.mode_selector.currentIndexChanged.connect(self._emit_change)
        root.addWidget(self.mode_selector)

        # --------------------------------------------------------------
        # CORE SLIDERS
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Core Parameters"))

        self.prompt_accuracy = LabeledSlider(
            "Prompt Accuracy",
            "How strictly the AI follows the prompt",
            default=75,
        )
        self.reference_strength = LabeledSlider(
            "Reference Influence",
            "How strongly reference audio/images affect output",
            default=60,
        )
        self.creativity = LabeledSlider(
            "Creativity / Novelty",
            "Degree of deviation from learned patterns",
            default=45,
        )

        self.prompt_accuracy.valueChanged.connect(self._emit_change)
        self.reference_strength.valueChanged.connect(self._emit_change)
        self.creativity.valueChanged.connect(self._emit_change)

        root.addWidget(self.prompt_accuracy)
        root.addWidget(self.reference_strength)
        root.addWidget(self.creativity)

        # --------------------------------------------------------------
        # QUALITY & POST
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Quality & Post-Processing"))

        self.mastering = QCheckBox("Automatic studio mastering (Hi-Fi)")
        self.mastering.setChecked(True)
        self.mastering.stateChanged.connect(self._emit_change)

        self.noise_cleanup = QCheckBox("Remove artifacts / neural noise")
        self.noise_cleanup.setChecked(True)
        self.noise_cleanup.stateChanged.connect(self._emit_change)

        self.stereo_enhance = QCheckBox("Wide stereo enhancement")
        self.stereo_enhance.setChecked(True)
        self.stereo_enhance.stateChanged.connect(self._emit_change)

        root.addWidget(self.mastering)
        root.addWidget(self.noise_cleanup)
        root.addWidget(self.stereo_enhance)

        # --------------------------------------------------------------
        # ADVANCED BEHAVIOR
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Advanced Behavior"))

        self.iterative_refinement = QCheckBox(
            "Multi-pass generation (best-of-N selection)"
        )
        self.iterative_refinement.stateChanged.connect(self._emit_change)

        self.humanization = QCheckBox(
            "Humanize timing, dynamics & micro-imperfections"
        )
        self.humanization.setChecked(True)
        self.humanization.stateChanged.connect(self._emit_change)

        root.addWidget(self.iterative_refinement)
        root.addWidget(self.humanization)

        root.addStretch()

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def get_payload(self) -> Dict[str, object]:
        """
        Export structured generation control payload.

        This payload is consumed by:
        - semantic engine
        - generation backend
        """
        return {
            "mode": self.mode_selector.currentText(),
            "prompt_accuracy": self.prompt_accuracy.value(),
            "reference_strength": self.reference_strength.value(),
            "creativity": self.creativity.value(),
            "post_processing": {
                "mastering": self.mastering.isChecked(),
                "noise_cleanup": self.noise_cleanup.isChecked(),
                "stereo_enhance": self.stereo_enhance.isChecked(),
            },
            "advanced": {
                "iterative_refinement": self.iterative_refinement.isChecked(),
                "humanization": self.humanization.isChecked(),
            },
        }

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _emit_change(self) -> None:
        payload = self.get_payload()
        self.controls_changed.emit(payload)
        self._signals.generation_controls_updated.emit(payload)


# =============================================================================
# COMPONENTS
# =============================================================================

class SectionLabel(QLabel):
    def __init__(self, text: str):
        super().__init__(text)
        self.setObjectName("GenerationSectionLabel")


class LabeledSlider(QFrame):
    """
    Slider with explanation and numeric feedback.
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
        self.label.setObjectName("GenerationSliderTitle")
        layout.addWidget(self.label)

        desc = QLabel(description)
        desc.setObjectName("GenerationSliderDescription")
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
