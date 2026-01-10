"""
NOSIS – Library Search Bar
=========================

Enterprise-grade intelligent search & filtering component (2025–2026).

Purpose:
- High-performance search across generated assets
- Semantic-ready query input
- Multi-criteria filtering orchestration
- UX-first, latency-free interaction

This module defines HOW users FIND content in large libraries.
"""

from __future__ import annotations

import logging
from typing import Dict

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QLabel,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.search_bar")


class LibrarySearchBar(QFrame):
    """
    Intelligent search & filter bar for LibraryPanel.

    Responsibilities:
    - Text-based search
    - Primary filter selection
    - Emission of structured search queries
    - Preparation for semantic search expansion
    """

    search_changed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()

        self.setObjectName("LibrarySearchBar")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._init_ui()

        logger.info("LibrarySearchBar initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by title, style, mood, voice…"
        )
        self.search_input.textChanged.connect(self._emit_change)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All",
            "Recent",
            "Favorites",
            "With vocals",
            "Instrumental",
            "High quality",
        ])
        self.filter_combo.currentIndexChanged.connect(self._emit_change)

        layout.addWidget(self.search_input)
        layout.addWidget(self.filter_combo)

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def get_payload(self) -> Dict[str, str]:
        """
        Structured search payload.

        Ready for:
        - simple filtering
        - backend queries
        - semantic search engine
        """
        return {
            "query": self.search_input.text().strip(),
            "filter": self.filter_combo.currentText(),
        }

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _emit_change(self) -> None:
        payload = self.get_payload()
        self.search_changed.emit(payload)
        self._signals.library_search_updated.emit(payload)
