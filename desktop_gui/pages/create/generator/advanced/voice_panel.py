"""
NOSIS – Advanced Voice Panel
============================

Enterprise-grade vocal design & control system (2025–2026).

Purpose:
- Fine-grained control over vocal identity
- Human-like vocal variability
- Language, accent, emotion & imperfection modeling
- Choir & multi-voice orchestration
- Semantic-ready payload for generation backend

This module defines WHO is singing and HOW they sing.
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
    QTextEdit,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.voice_panel")


# =============================================================================
# VOICE PANEL
# =============================================================================

class VoicePanel(QFrame):
    """
    Advanced vocal configuration panel.

    Covers:
    - Voice identity
    - Gender / age / timbre
    - Language & accent
    - Emotional delivery
    - Human imperfections
    - Choir / stack logic
    """

    voice_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()

        self.setObjectName("VoicePanel")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._init_ui()

        logger.info("VoicePanel initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        # --------------------------------------------------------------
        # VOICE IDENTITY
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Voice Identity"))

        self.voice_type = QComboBox()
        self.voice_type.addItems([
            "Natural / Neutral",
            "Pop Vocal",
            "Rock Vocal",
            "Opera / Classical",
            "Rap / Spoken",
            "Cinematic / Epic",
            "Experimental / Synthetic",
        ])
        self.voice_type.currentIndexChanged.connect(self._emit_change)
        root.addWidget(self.voice_type)

        # --------------------------------------------------------------
        # GENDER & AGE
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Gender & Age"))

        gender_row = QHBoxLayout()
        self.gender = QComboBox()
        self.gender.addItems([
            "Auto",
            "Male",
            "Female",
            "Androgynous",
            "Child",
        ])
        self.gender.currentIndexChanged.connect(self._emit_change)

        self.age = QSlider(Qt.Orientation.Horizontal)
        self.age.setRange(10, 80)
        self.age.setValue(30)
        self.age.valueChanged.connect(self._emit_change)

        gender_row.addWidget(QLabel("Gender"))
        gender_row.addWidget(self.gender)
        gender_row.addSpacing(12)
        gender_row.addWidget(QLabel("Age"))
        gender_row.addWidget(self.age)

        root.addLayout(gender_row)

        # --------------------------------------------------------------
        # LANGUAGE & ACCENT
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Language & Accent"))

        lang_row = QHBoxLayout()

        self.language = QComboBox()
        self.language.addItems([
            "Auto",
            "English",
            "Spanish",
            "French",
            "German",
            "Italian",
            "Russian",
            "Japanese",
            "Korean",
            "Chinese",
            "Portuguese",
            "Arabic",
        ])
        self.language.currentIndexChanged.connect(self._emit_change)

        self.accent = QComboBox()
        self.accent.addItems([
            "Neutral",
            "American",
            "British",
            "European",
            "Latin",
            "Asian",
            "Regional / Local",
        ])
        self.accent.currentIndexChanged.connect(self._emit_change)

        lang_row.addWidget(self.language)
        lang_row.addWidget(self.accent)

        root.addLayout(lang_row)

        # --------------------------------------------------------------
        # EMOTION & DELIVERY
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Emotion & Delivery"))

        self.emotion = QComboBox()
        self.emotion.addItems([
            "Neutral",
            "Sad",
            "Happy",
            "Aggressive",
            "Intimate",
            "Dark",
            "Epic",
            "Hopeful",
            "Angry",
            "Melancholic",
        ])
        self.emotion.currentIndexChanged.connect(self._emit_change)
        root.addWidget(self.emotion)

        self.delivery_intensity = LabeledSlider(
            "Delivery Intensity",
            "How strong and expressive the vocal delivery is",
            default=60,
        )
        self.delivery_intensity.valueChanged.connect(self._emit_change)
        root.addWidget(self.delivery_intensity)

        # --------------------------------------------------------------
        # HUMANIZATION
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Human Imperfections"))

        self.pitch_instability = LabeledSlider(
            "Pitch Instability",
            "Micro pitch variations like real singers",
            default=25,
        )
        self.timing_drift = LabeledSlider(
            "Timing Drift",
            "Natural rhythm imperfections",
            default=30,
        )
        self.breathiness = LabeledSlider(
            "Breathiness",
            "Audible breathing & air noise",
            default=40,
        )

        for s in (
            self.pitch_instability,
            self.timing_drift,
            self.breathiness,
        ):
            s.valueChanged.connect(self._emit_change)
            root.addWidget(s)

        # --------------------------------------------------------------
        # CHOIR / STACK
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Choir / Voice Stack"))

        self.choir_enabled = QCheckBox("Enable choir / multi-voice stack")
        self.choir_enabled.stateChanged.connect(self._emit_change)
        root.addWidget(self.choir_enabled)

        self.choir_size = LabeledSlider(
            "Choir Size",
            "Number of voices layered together",
            default=4,
        )
        self.choir_size.valueChanged.connect(self._emit_change)
        root.addWidget(self.choir_size)

        # --------------------------------------------------------------
        # PRONUNCIATION NOTES
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Pronunciation Notes"))

        self.pronunciation_notes = QTextEdit()
        self.pronunciation_notes.setPlaceholderText(
            "Optional notes for pronunciation, phonetics or emphasis.\n"
            "Example:\n"
            "- Roll the R in Spanish words\n"
            "- Softer consonants in verses\n"
        )
        self.pronunciation_notes.textChanged.connect(self._emit_change)
        root.addWidget(self.pronunciation_notes)

        root.addStretch()

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def get_payload(self) -> Dict[str, object]:
        """
        Structured vocal configuration payload.
        """
        return {
            "voice_type": self.voice_type.currentText(),
            "gender": self.gender.currentText(),
            "age": self.age.value(),
            "language": self.language.currentText(),
            "accent": self.accent.currentText(),
            "emotion": self.emotion.currentText(),
            "delivery_intensity": self.delivery_intensity.value(),
            "humanization": {
                "pitch_instability": self.pitch_instability.value(),
                "timing_drift": self.timing_drift.value(),
                "breathiness": self.breathiness.value(),
            },
            "choir": {
                "enabled": self.choir_enabled.isChecked(),
                "size": self.choir_size.value(),
            },
            "pronunciation_notes": self.pronunciation_notes.toPlainText(),
        }

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _emit_change(self) -> None:
        payload = self.get_payload()
        self.voice_changed.emit(payload)
        self._signals.voice_config_updated.emit(payload)


# =============================================================================
# COMPONENTS
# =============================================================================

class SectionLabel(QLabel):
    def __init__(self, text: str):
        super().__init__(text)
        self.setObjectName("VoiceSectionLabel")


class LabeledSlider(QFrame):
    """
    Slider with title, description and value feedback.
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
        self.label.setObjectName("VoiceSliderTitle")
        layout.addWidget(self.label)

        desc = QLabel(description)
        desc.setObjectName("VoiceSliderDescription")
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
