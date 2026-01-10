"""
NOSIS – Batch Group Controller
=============================

Enterprise-grade batch selection & group operations module (2025–2026).

Purpose:
- Enable batch operations on multiple tracks
- Provide DAW-style multi-selection workflows
- Support bulk actions: regenerate, export, tag, delete, send to Studio
- Foundation for enterprise-scale productivity

BatchGroup is NOT a helper.
It is a control surface for mass operations.
"""

from __future__ import annotations

import logging
from typing import List, Dict

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.batch_group")


class BatchGroup(QFrame):
    """
    Batch group controller for Library.

    Responsibilities:
    - Track multi-selection state
    - Expose bulk actions
    - Emit structured batch commands
    - Coordinate with backend & Studio
    """

    selection_changed = pyqtSignal(list)
    batch_action_requested = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()
        self._selected_ids: List[str] = []

        self.setObjectName("BatchGroup")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self._init_ui()

        logger.info("BatchGroup initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        self.info_label = QLabel("No tracks selected")
        root.addWidget(self.info_label)

        actions = QHBoxLayout()

        self.regenerate_btn = QPushButton("Batch Regenerate")
        self.open_studio_btn = QPushButton("Open in Studio")
        self.export_btn = QPushButton("Export")
        self.delete_btn = QPushButton("Delete")

        self.regenerate_btn.clicked.connect(
            lambda: self._emit_action("regenerate")
        )
        self.open_studio_btn.clicked.connect(
            lambda: self._emit_action("open_studio")
        )
        self.export_btn.clicked.connect(
            lambda: self._emit_action("export")
        )
        self.delete_btn.clicked.connect(
            lambda: self._emit_action("delete")
        )

        actions.addWidget(self.regenerate_btn)
        actions.addWidget(self.open_studio_btn)
        actions.addWidget(self.export_btn)
        actions.addWidget(self.delete_btn)

        root.addLayout(actions)

        self._update_state()

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def set_selection(self, track_ids: List[str]) -> None:
        self._selected_ids = list(track_ids)
        self._update_state()

        self.selection_changed.emit(self._selected_ids)
        self._signals.batch_selection_updated.emit(self._selected_ids)

    def clear_selection(self) -> None:
        self.set_selection([])

    # ------------------------------------------------------------------
    # INTERNAL
    # ------------------------------------------------------------------

    def _update_state(self) -> None:
        count = len(self._selected_ids)

        if count == 0:
            self.info_label.setText("No tracks selected")
            self._set_actions_enabled(False)
        else:
            self.info_label.setText(f"Selected tracks: {count}")
            self._set_actions_enabled(True)

    def _set_actions_enabled(self, enabled: bool) -> None:
        self.regenerate_btn.setEnabled(enabled)
        self.open_studio_btn.setEnabled(enabled)
        self.export_btn.setEnabled(enabled)
        self.delete_btn.setEnabled(enabled)

    def _emit_action(self, action: str) -> None:
        payload = {
            "action": action,
            "track_ids": list(self._selected_ids),
        }

        logger.debug("Batch action requested: %s", payload)

        self.batch_action_requested.emit(payload)
        self._signals.batch_action_requested.emit(payload)
