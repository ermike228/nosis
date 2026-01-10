"""
NOSIS – Advanced Mastering Panel
================================

Enterprise-grade AI mastering & post-production control system (2025–2026).

Purpose:
- Studio-grade automatic mastering
- Loudness, dynamics & spectral control
- Genre-aware mastering profiles
- Artifact & neural noise suppression
- Final quality gate before export

This module defines HOW the final audio is polished.
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
    QComboBox,
    QSlider,
    QCheckBox,
    QSizePolicy,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.mastering_panel")


# =============================================================================
# MASTERING PANEL
# =============================================================================

class MasteringPanel(QFrame):
    """
    Advanced mastering configuration panel.

    Covers:
    - Loudness & dynamic range
    - EQ balance & tonal shaping
    - Stereo image control
    - Artifact suppression
    - Release-ready quality profiles
    """

    mastering_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()

        self.setObjectName("MasteringPanel")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._init_ui()

        logger.info("MasteringPanel initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        # --------------------------------------------------------------
        # MASTERING PROFILE
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Mastering Profile"))

        self.profile = QComboBox()
        self.profile.addItems([
            "Auto (AI decides)",
            "Streaming (Spotify / Apple Music)",
            "Club / EDM Loud",
            "Cinematic / Film Score",
            "Broadcast / TV",
            "Vinyl / Analog",
            "Audiophile / Hi-Fi",
        ])
        self.profile.currentIndexChanged.connect(self._emit_change)
        root.addWidget(self.profile)

        # --------------------------------------------------------------
        # LOUDNESS & DYNAMICS
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Loudness & Dynamics"))

        self.target_lufs = LabeledSlider(
            "Target Loudness (LUFS)",
            "Overall perceived loudness of the track",
            default=65,
        )
        self.dynamic_range = LabeledSlider(
            "Dynamic Range",
            "Difference between quiet and loud parts",
            default=55,
        )

        self.target_lufs.valueChanged.connect(self._emit_change)
        self.dynamic_range.valueChanged.connect(self._emit_change)

        root.addWidget(self.target_lufs)
        root.addWidget(self.dynamic_range)

        # --------------------------------------------------------------
        # TONAL BALANCE
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Tonal Balance"))

        self.low_balance = LabeledSlider(
            "Low Frequencies",
            "Bass weight and low-end fullness",
            default=50,
        )
        self.mid_balance = LabeledSlider(
            "Mid Frequencies",
            "Clarity of vocals and instruments",
            default=55,
        )
        self.high_balance = LabeledSlider(
            "High Frequencies",
            "Air, brightness and detail",
            default=60,
        )

        for s in (
            self.low_balance,
            self.mid_balance,
            self.high_balance,
        ):
            s.valueChanged.connect(self._emit_change)
            root.addWidget(s)

        # --------------------------------------------------------------
        # STEREO IMAGE
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Stereo Image"))

        self.stereo_width = LabeledSlider(
            "Stereo Width",
            "Perceived horizontal width of the mix",
            default=65,
        )
        self.center_focus = LabeledSlider(
            "Center Focus",
            "How strong vocals and core elements stay in center",
            default=60,
        )

        self.stereo_width.valueChanged.connect(self._emit_change)
        self.center_focus.valueChanged.connect(self._emit_change)

        root.addWidget(self.stereo_width)
        root.addWidget(self.center_focus)

        # --------------------------------------------------------------
        # ARTIFACT CONTROL
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Artifact & Noise Control"))

        self.artifact_removal = QCheckBox(
            "Suppress neural artifacts & digital harshness"
        )
        self.artifact_removal.setChecked(True)
        self.artifact_removal.stateChanged.connect(self._emit_change)

        self.de_essing = QCheckBox(
            "Automatic de-essing (harsh sibilants)"
        )
        self.de_essing.setChecked(True)
        self.de_essing.stateChanged.connect(self._emit_change)

        self.transient_smoothing = QCheckBox(
            "Transient smoothing (reduce clicks & spikes)"
        )
        self.transient_smoothing.setChecked(True)
        self.transient_smoothing.stateChanged.connect(self._emit_change)

        root.addWidget(self.artifact_removal)
        root.addWidget(self.de_essing)
        root.addWidget(self.transient_smoothing)

        # --------------------------------------------------------------
        # FINAL QUALITY GATE
        # --------------------------------------------------------------

        root.addWidget(SectionLabel("Final Quality Gate"))

        self.release_ready = QCheckBox(
            "Enforce release-ready quality (reject weak outputs)"
        )
        self.release_ready.setChecked(True)
        self.release_ready.stateChanged.connect(self._emit_change)

        self.true_peak_protection = QCheckBox(
            "True-peak protection (no clipping)"
        )
        self.true_peak_protection.setChecked(True)
        self.true_peak_protection.stateChanged.connect(self._emit_change)

        root.addWidget(self.release_ready)
        root.addWidget(self.true_peak_protection)

        root.addStretch()

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def get_payload(self) -> Dict[str, object]:
        """
        Structured mastering payload for backend & semantic engine.
        """
        return {
            "profile": self.profile.currentText(),
            "loudness": {
                "target_lufs": self.target_lufs.value(),
                "dynamic_range": self.dynamic_range.value(),
            },
            "tonal_balance": {
                "low": self.low_balance.value(),
                "mid": self.mid_balance.value(),
                "high": self.high_balance.value(),
            },
            "stereo": {
                "width": self.stereo_width.value(),
                "center_focus": self.center_focus.value(),
            },
            "artifact_control": {
                "artifact_removal": self.artifact_removal.isChecked(),
                "de_essing": self.de_essing.isChecked(),
                "transient_smoothing": self.transient_smoothing.isChecked(),
            },
            "quality_gate": {
                "release_ready": self.release_ready.isChecked(),
                "true_peak_protection": self.true_peak_protection.isChecked(),
            },
        }

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _emit_change(self) -> None:
        payload = self.get_payload()
        self.mastering_changed.emit(payload)
        self._signals.mastering_config_updated.emit(payload)


# =============================================================================
# COMPONENTS
# =============================================================================

class SectionLabel(QLabel):
    def __init__(self, text: str):
        super().__init__(text)
        self.setObjectName("MasteringSectionLabel")


class LabeledSlider(QFrame):
    """
    Slider with mastering semantics and numeric feedback.
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
        self.label.setObjectName("MasteringSliderTitle")
        layout.addWidget(self.label)

        desc = QLabel(description)
        desc.setObjectName("MasteringSliderDescription")
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
