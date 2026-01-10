"""
NOSIS Desktop GUI – Reference Bar
================================

Enterprise-grade reference management bar (2025–2026).

Purpose:
- Attach reference audio / images to generation
- Support multi-reference workflows
- Drag & drop UX
- Per-reference enable / disable
- Preparation for similarity-weighted generation

This component is used inside Create → Generator panel.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QFileDialog,
)

from desktop_gui.bridge.file_bridge import get_file_bridge
from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.reference_bar")


# =============================================================================
# REFERENCE BAR
# =============================================================================

class ReferenceBar(QFrame):
    """
    Horizontal reference attachment bar.

    Features:
    - Drag & drop files
    - Add / remove references
    - Enable / disable references
    - Emits structured reference payload
    """

    references_changed = pyqtSignal(list)

    def __init__(self, category: str = "audio"):
        super().__init__()

        self.category = category
        self._file_bridge = get_file_bridge()
        self._signals = get_signals()

        self.setObjectName("ReferenceBar")
        self.setAcceptDrops(True)

        self._references: List[ReferenceItem] = []

        self._init_ui()

        logger.info("ReferenceBar initialized (%s)", category)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("References")
        title.setObjectName("ReferenceBarTitle")

        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._open_file_dialog)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(add_btn)

        layout.addLayout(header)

        self.list = QListWidget()
        self.list.setObjectName("ReferenceList")
        layout.addWidget(self.list)

        hint = QLabel("Drag & drop reference files here")
        hint.setObjectName("ReferenceHint")
        layout.addWidget(hint)

    # ------------------------------------------------------------------
    # FILE HANDLING
    # ------------------------------------------------------------------

    def _open_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select reference files",
            "",
            "Audio Files (*.wav *.mp3 *.flac);;Images (*.png *.jpg *.webp)",
        )

        if files:
            self._handle_new_files([Path(f) for f in files])

    def _handle_new_files(self, paths: List[Path]):
        for path in paths:
            self._add_reference(path)

        self._emit_references_changed()

    # ------------------------------------------------------------------
    # REFERENCES
    # ------------------------------------------------------------------

    def _add_reference(self, path: Path):
        item = ReferenceItem(path)
        self._references.append(item)

        widget_item = QListWidgetItem()
        widget_item.setSizeHint(item.sizeHint())

        self.list.addItem(widget_item)
        self.list.setItemWidget(widget_item, item)

        item.removed.connect(lambda: self._remove_reference(item))

    def _remove_reference(self, item: "ReferenceItem"):
        index = self._references.index(item)
        self._references.remove(item)
        self.list.takeItem(index)
        self._emit_references_changed()

    def get_active_references(self) -> List[dict]:
        """
        Structured reference payload for generation.
        """
        return [
            ref.to_payload()
            for ref in self._references
            if ref.enabled
        ]

    def _emit_references_changed(self):
        self.references_changed.emit(self.get_active_references())

    # ------------------------------------------------------------------
    # DRAG & DROP
    # ------------------------------------------------------------------

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = [
            Path(url.toLocalFile())
            for url in event.mimeData().urls()
        ]
        self._handle_new_files(paths)


# =============================================================================
# REFERENCE ITEM
# =============================================================================

class ReferenceItem(QFrame):
    """
    Single reference entry.

    Supports:
    - enable / disable
    - removal
    - future similarity weighting
    """

    removed = pyqtSignal()

    def __init__(self, path: Path):
        super().__init__()

        self.path = path
        self.enabled = True

        self.setObjectName("ReferenceItem")

        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        self.label = QLabel(self.path.name)
        self.label.setObjectName("ReferenceItemLabel")

        toggle = QPushButton("✓")
        toggle.setFixedWidth(24)
        toggle.clicked.connect(self._toggle_enabled)

        remove = QPushButton("✕")
        remove.setFixedWidth(24)
        remove.clicked.connect(self.removed.emit)

        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(toggle)
        layout.addWidget(remove)

    def _toggle_enabled(self):
        self.enabled = not self.enabled
        self.setProperty("disabled", not self.enabled)
        self.style().polish(self)

    def to_payload(self) -> dict:
        return {
            "filename": self.path.name,
            "path": str(self.path),
            "enabled": self.enabled,
        }
