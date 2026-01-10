"""
NOSIS – Exports Manager
======================

Enterprise-grade export orchestration module for NOSIS Library (2025–2026).

Purpose:
- Centralized control of all export workflows
- Support for professional delivery formats (music, stems, visuals)
- Batch and playlist-based exports
- Deterministic, reproducible, auditable export pipeline

Exports is NOT a file-save dialog.
It is a production delivery system.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QComboBox,
    QCheckBox,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.exports")


class Exports(QWidget):
    """
    Export orchestration panel.

    Responsibilities:
    - Define WHAT is exported (tracks / playlists / batches)
    - Define HOW it is exported (format, quality, stems)
    - Emit export jobs as structured payloads
    - Integrate with Studio render engine and backend queues
    """

    export_requested = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()

        self._context: Dict = {}

        self.setObjectName("Exports")

        self._init_ui()

        logger.info("Exports initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        # --------------------------------------------------------------
        # TARGET
        # --------------------------------------------------------------

        target_group = QGroupBox("Export Target")
        target_layout = QVBoxLayout(target_group)

        self.target_selector = QComboBox()
        self.target_selector.addItems([
            "Selected Track",
            "Batch Selection",
            "Playlist",
        ])

        target_layout.addWidget(self.target_selector)
        root.addWidget(target_group)

        # --------------------------------------------------------------
        # FORMAT
        # --------------------------------------------------------------

        format_group = QGroupBox("Audio Format")
        format_layout = QVBoxLayout(format_group)

        self.format_selector = QComboBox()
        self.format_selector.addItems([
            "WAV 24-bit",
            "WAV 32-bit float",
            "FLAC",
            "MP3 320kbps",
        ])

        format_layout.addWidget(self.format_selector)
        root.addWidget(format_group)

        # --------------------------------------------------------------
        # STEMS
        # --------------------------------------------------------------

        stems_group = QGroupBox("Stems & Options")
        stems_layout = QVBoxLayout(stems_group)

        self.export_stems = QCheckBox("Export stems")
        self.include_master = QCheckBox("Include master track")
        self.normalize = QCheckBox("Normalize loudness")

        stems_layout.addWidget(self.export_stems)
        stems_layout.addWidget(self.include_master)
        stems_layout.addWidget(self.normalize)

        root.addWidget(stems_group)

        # --------------------------------------------------------------
        # ACTION
        # --------------------------------------------------------------

        action_row = QHBoxLayout()

        self.export_btn = QPushButton("Start Export")
        self.export_btn.clicked.connect(self._emit_export)

        action_row.addStretch()
        action_row.addWidget(self.export_btn)

        root.addLayout(action_row)
        root.addStretch()

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def set_context(self, context: Dict) -> None:
        """
        Context defines which tracks / playlists are currently active.
        """
        self._context = context

    # ------------------------------------------------------------------
    # INTERNAL
    # ------------------------------------------------------------------

    def _emit_export(self) -> None:
        payload = {
            "target": self.target_selector.currentText(),
            "format": self.format_selector.currentText(),
            "stems": self.export_stems.isChecked(),
            "include_master": self.include_master.isChecked(),
            "normalize": self.normalize.isChecked(),
            "context": self._context,
        }

        logger.debug("Export requested: %s", payload)

        self.export_requested.emit(payload)
        self._signals.export_requested.emit(payload)
