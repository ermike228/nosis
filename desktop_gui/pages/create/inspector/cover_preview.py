"""
NOSIS – Cover Preview
====================

Enterprise-grade cover artwork preview for Inspector Panel (2025–2026).

Purpose:
- Visual identity anchor for generated track
- Display AI-generated 4K artwork safely and efficiently
- Provide quick actions: regenerate, export, replace
- Bridge between music generation and visual storytelling

CoverPreview is NOT an image widget.
It is a visual control surface.
"""

from __future__ import annotations

import logging
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.cover_preview")


class CoverPreview(QFrame):
    """
    Displays and manages the cover artwork of the selected track.

    Responsibilities:
    - Render high-resolution images safely
    - Handle empty / loading states
    - Provide contextual actions for artwork
    - Emit structured events, not logic
    """

    regenerate_requested = pyqtSignal(str)
    replace_requested = pyqtSignal(str)
    export_requested = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()
        self._track_id: Optional[str] = None
        self._image_path: Optional[str] = None

        self.setObjectName("CoverPreview")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumHeight(240)

        self._init_ui()

        logger.info("CoverPreview initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        self.image_label = QLabel("No cover available")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(True)
        self.image_label.setMinimumHeight(180)

        root.addWidget(self.image_label)

        actions = QHBoxLayout()

        self.regen_btn = QPushButton("Regenerate")
        self.replace_btn = QPushButton("Replace")
        self.export_btn = QPushButton("Export")

        self.regen_btn.clicked.connect(self._on_regenerate)
        self.replace_btn.clicked.connect(self._on_replace)
        self.export_btn.clicked.connect(self._on_export)

        actions.addWidget(self.regen_btn)
        actions.addWidget(self.replace_btn)
        actions.addWidget(self.export_btn)

        root.addLayout(actions)

        self._set_enabled(False)

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def set_cover(self, track_id: str, image_path: Optional[str]) -> None:
        self._track_id = track_id
        self._image_path = image_path

        if image_path:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                self.image_label.setText("Failed to load image")
            else:
                self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("No cover available")

        self._set_enabled(True)

    def clear(self) -> None:
        self._track_id = None
        self._image_path = None
        self.image_label.setText("No cover available")
        self._set_enabled(False)

    # ------------------------------------------------------------------
    # INTERNAL
    # ------------------------------------------------------------------

    def _set_enabled(self, enabled: bool) -> None:
        self.regen_btn.setEnabled(enabled)
        self.replace_btn.setEnabled(enabled)
        self.export_btn.setEnabled(enabled)

    # ------------------------------------------------------------------
    # EVENTS
    # ------------------------------------------------------------------

    def _on_regenerate(self) -> None:
        if not self._track_id:
            return
        self.regenerate_requested.emit(self._track_id)
        self._signals.regenerate_cover_requested.emit(self._track_id)

    def _on_replace(self) -> None:
        if not self._track_id:
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select cover image",
            "",
            "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if file_path:
            self.replace_requested.emit(file_path)
            self._signals.replace_cover_requested.emit({
                "track_id": self._track_id,
                "path": file_path,
            })

    def _on_export(self) -> None:
        if not self._track_id or not self._image_path:
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export cover image",
            "cover.png",
            "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if save_path:
            self.export_requested.emit(save_path)
            self._signals.export_cover_requested.emit({
                "track_id": self._track_id,
                "path": save_path,
            })
