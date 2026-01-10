"""
NOSIS – Advanced Model Panel
===========================

Enterprise-grade AI model orchestration & selection panel (2025–2026).

Purpose:
- Explicit control over AI model selection and behavior
- Multi-model routing (music, vocal, composition, mastering)
- Quality vs speed trade-offs
- Compute budget governance
- Deterministic vs exploratory generation
- Enterprise-ready experimentation layer

This module defines WHICH intelligence generates the music
and HOW resources are allocated.
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
    QSlider,
    QCheckBox,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.model_panel")


class ModelPanel(QFrame):
    """
    Advanced AI model configuration panel.
    """

    model_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._signals = get_signals()
        self.setObjectName("ModelPanel")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self._init_ui()

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        root.addWidget(QLabel("Model Family"))
        self.model_family = QComboBox()
        self.model_family.addItems([
            "Auto (AI selects best)",
            "NOSIS-Core",
            "NOSIS-Pro",
            "NOSIS-Studio",
            "Experimental / Research",
        ])
        self.model_family.currentIndexChanged.connect(self._emit_change)
        root.addWidget(self.model_family)

        root.addWidget(QLabel("Model Version"))
        self.model_version = QComboBox()
        self.model_version.addItems([
            "Latest Stable",
            "Previous Stable",
            "Canary / Preview",
            "Long-Term Support (LTS)",
        ])
        self.model_version.currentIndexChanged.connect(self._emit_change)
        root.addWidget(self.model_version)

        root.addWidget(QLabel("Quality Priority"))
        self.quality_speed = QSlider(Qt.Orientation.Horizontal)
        self.quality_speed.setRange(0, 100)
        self.quality_speed.setValue(70)
        self.quality_speed.valueChanged.connect(self._emit_change)
        root.addWidget(self.quality_speed)

        root.addWidget(QLabel("Compute Budget"))
        self.compute_budget = QSlider(Qt.Orientation.Horizontal)
        self.compute_budget.setRange(0, 100)
        self.compute_budget.setValue(60)
        self.compute_budget.valueChanged.connect(self._emit_change)
        root.addWidget(self.compute_budget)

        root.addWidget(QLabel("Sampling Strategy"))
        self.sampling_method = QComboBox()
        self.sampling_method.addItems([
            "Balanced",
            "High diversity",
            "Low randomness",
            "Deterministic",
            "Exploratory",
        ])
        self.sampling_method.currentIndexChanged.connect(self._emit_change)
        root.addWidget(self.sampling_method)

        self.lock_seed = QCheckBox("Lock random seed")
        self.lock_seed.stateChanged.connect(self._emit_change)
        root.addWidget(self.lock_seed)

        self.exploration_boost = QCheckBox("Exploration boost")
        self.exploration_boost.stateChanged.connect(self._emit_change)
        root.addWidget(self.exploration_boost)

        self.multi_pass = QCheckBox("Enable multi-pass generation")
        self.multi_pass.setChecked(True)
        self.multi_pass.stateChanged.connect(self._emit_change)
        root.addWidget(self.multi_pass)

        self.fallback_enabled = QCheckBox("Enable fallback model")
        self.fallback_enabled.setChecked(True)
        self.fallback_enabled.stateChanged.connect(self._emit_change)
        root.addWidget(self.fallback_enabled)

        root.addStretch()

    def get_payload(self) -> Dict[str, object]:
        return {
            "model_family": self.model_family.currentText(),
            "model_version": self.model_version.currentText(),
            "quality_priority": self.quality_speed.value(),
            "compute_budget": self.compute_budget.value(),
            "sampling": self.sampling_method.currentText(),
            "determinism": {
                "lock_seed": self.lock_seed.isChecked(),
                "exploration_boost": self.exploration_boost.isChecked(),
            },
            "execution": {
                "multi_pass": self.multi_pass.isChecked(),
                "fallback_enabled": self.fallback_enabled.isChecked(),
            },
        }

    def _emit_change(self) -> None:
        payload = self.get_payload()
        self.model_changed.emit(payload)
        self._signals.model_config_updated.emit(payload)
