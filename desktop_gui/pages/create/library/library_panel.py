"""
NOSIS – Library Panel
====================

Enterprise-grade generated content library & asset management system (2025–2026).

Purpose:
- Display and manage generated tracks
- Fast search, filtering and selection
- Versioning and metadata awareness
- Integration with inspector & playback
- Foundation for professional workflow

This module defines HOW generated content is ORGANIZED and ACCESSED.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QComboBox,
    QPushButton,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.library_panel")


class LibraryPanel(QFrame):
    """
    Generated tracks library panel.

    Responsibilities:
    - Track listing
    - Search & filtering
    - Selection & activation
    - Metadata handoff to inspector
    """

    track_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()
        self._tracks: List[Dict] = []

        self.setObjectName("LibraryPanel")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._init_ui()
        self._bind_signals()

        logger.info("LibraryPanel initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        # --------------------------------------------------------------
        # SEARCH & FILTERS
        # --------------------------------------------------------------

        search_row = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tracks…")
        self.search_input.textChanged.connect(self._refresh_list)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All",
            "Recent",
            "Favorites",
            "With vocals",
            "Instrumental",
        ])
        self.filter_combo.currentIndexChanged.connect(self._refresh_list)

        search_row.addWidget(self.search_input)
        search_row.addWidget(self.filter_combo)

        root.addLayout(search_row)

        # --------------------------------------------------------------
        # TRACK LIST
        # --------------------------------------------------------------

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_selected)
        root.addWidget(self.list_widget)

        # --------------------------------------------------------------
        # ACTIONS
        # --------------------------------------------------------------

        action_row = QHBoxLayout()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._refresh_list)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._delete_selected)

        action_row.addWidget(self.refresh_button)
        action_row.addWidget(self.delete_button)

        root.addLayout(action_row)

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _bind_signals(self) -> None:
        self._signals.track_added.connect(self._on_track_added)
        self._signals.library_updated.connect(self._refresh_list)

    # ------------------------------------------------------------------
    # DATA MANAGEMENT
    # ------------------------------------------------------------------

    def set_tracks(self, tracks: List[Dict]) -> None:
        """
        Replace entire library dataset.
        """
        self._tracks = tracks
        self._refresh_list()

    def add_track(self, track: Dict) -> None:
        """
        Add a single track to the library.
        """
        self._tracks.insert(0, track)
        self._refresh_list()

    # ------------------------------------------------------------------
    # INTERNAL LOGIC
    # ------------------------------------------------------------------

    def _refresh_list(self) -> None:
        query = self.search_input.text().lower()
        filter_mode = self.filter_combo.currentText()

        self.list_widget.clear()

        for track in self._filtered_tracks(query, filter_mode):
            item = QListWidgetItem(track.get("title", "Untitled"))
            item.setData(Qt.ItemDataRole.UserRole, track)
            self.list_widget.addItem(item)

    def _filtered_tracks(self, query: str, filter_mode: str) -> List[Dict]:
        results = []

        for track in self._tracks:
            title = track.get("title", "").lower()

            if query and query not in title:
                continue

            if filter_mode == "With vocals" and not track.get("has_vocals"):
                continue

            if filter_mode == "Instrumental" and track.get("has_vocals"):
                continue

            results.append(track)

        return results

    def _on_item_selected(self, item: QListWidgetItem) -> None:
        track = item.data(Qt.ItemDataRole.UserRole)
        self.track_selected.emit(track)
        self._signals.track_selected.emit(track.get("id"))

    def _delete_selected(self) -> None:
        item = self.list_widget.currentItem()
        if not item:
            return

        track = item.data(Qt.ItemDataRole.UserRole)
        track_id = track.get("id")

        self._tracks = [
            t for t in self._tracks if t.get("id") != track_id
        ]

        self._signals.track_deleted.emit(track_id)
        self._refresh_list()

    # ------------------------------------------------------------------
    # SIGNAL HANDLERS
    # ------------------------------------------------------------------

    def _on_track_added(self, track_id: str) -> None:
        """
        Placeholder hook for backend-driven updates.
        """
        self._refresh_list()
