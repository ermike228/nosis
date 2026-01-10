"""
NOSIS – Library Page
===================

Enterprise-grade Library Page for NOSIS (2025–2026).

Purpose:
- Central hub for all generated and imported assets
- Unified view across Create, Studio and external workflows
- Scalable to tens of thousands of tracks
- Acts as an operational workspace, not a passive list

LibraryPage is NOT a screen.
It is a production control center.
"""

from __future__ import annotations

import logging
from typing import List, Dict

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
)

from desktop_gui.pages.create.library.search_bar import SearchBar
from desktop_gui.pages.create.library.filters_panel import LibraryFiltersPanel
from desktop_gui.pages.create.library.track_card import TrackCard
from desktop_gui.pages.create.library.batch_group import BatchGroup
from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.library_page")


class LibraryPage(QWidget):
    """
    Main Library page.

    Responsibilities:
    - Orchestrate search, filters, batch and track cards
    - Reflect global library state
    - Act as navigation surface into Inspector and Studio
    """

    def __init__(self):
        super().__init__()

        self._signals = get_signals()
        self._tracks: List[Dict] = []

        self.setObjectName("LibraryPage")

        self._init_ui()
        self._bind_signals()

        logger.info("LibraryPage initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        # --------------------------------------------------------------
        # TOP CONTROLS
        # --------------------------------------------------------------

        top = QHBoxLayout()

        self.search_bar = SearchBar()
        self.filters_panel = LibraryFiltersPanel()

        top.addWidget(self.search_bar, 3)
        top.addWidget(self.filters_panel, 2)

        root.addLayout(top)

        # --------------------------------------------------------------
        # BATCH
        # --------------------------------------------------------------

        self.batch_group = BatchGroup()
        root.addWidget(self.batch_group)

        # --------------------------------------------------------------
        # TRACK LIST
        # --------------------------------------------------------------

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.list_layout.setSpacing(8)

        self.scroll.setWidget(self.list_container)
        root.addWidget(self.scroll)

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _bind_signals(self) -> None:
        self._signals.library_updated.connect(self.set_tracks)
        self._signals.track_selected.connect(self._on_track_selected)

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def set_tracks(self, tracks: List[Dict]) -> None:
        self._tracks = tracks
        self._rebuild()

    def _rebuild(self) -> None:
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for track in self._tracks:
            card = TrackCard(track)
            self.list_layout.addWidget(card)

        self.list_layout.addStretch()

    # ------------------------------------------------------------------
    # EVENTS
    # ------------------------------------------------------------------

    def _on_track_selected(self, track_id: str) -> None:
        self.batch_group.set_selection([track_id])
