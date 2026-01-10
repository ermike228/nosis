"""
NOSIS – Playlists Manager
========================

Enterprise-grade playlists and collections system for NOSIS Library (2025–2026).

Purpose:
- Logical grouping of tracks beyond folders
- Support for creative, functional and semantic playlists
- Foundation for workflows, releases, versions and collaboration
- Acts as an organizational brain for large libraries

Playlists is NOT a music player feature.
It is a professional asset-organization system.
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
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QInputDialog,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.playlists")


class Playlists(QWidget):
    """
    Playlists and collections manager.

    Responsibilities:
    - Create, rename and delete playlists
    - Assign tracks to multiple playlists
    - Expose playlist selection as navigation surface
    - Emit structured events for backend synchronization
    """

    playlist_selected = pyqtSignal(str)
    playlist_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()

        self._playlists: Dict[str, List[str]] = {}
        self._current_playlist: Optional[str] = None

        self.setObjectName("Playlists")

        self._init_ui()

        logger.info("Playlists initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        header = QHBoxLayout()
        header.addWidget(QLabel("Playlists"))
        header.addStretch()

        add_btn = QPushButton("+")
        add_btn.setFixedWidth(28)
        add_btn.clicked.connect(self._create_playlist)

        header.addWidget(add_btn)
        root.addLayout(header)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        root.addWidget(self.list_widget)

        actions = QHBoxLayout()

        self.rename_btn = QPushButton("Rename")
        self.delete_btn = QPushButton("Delete")

        self.rename_btn.clicked.connect(self._rename_playlist)
        self.delete_btn.clicked.connect(self._delete_playlist)

        actions.addWidget(self.rename_btn)
        actions.addWidget(self.delete_btn)

        root.addLayout(actions)

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def set_playlists(self, playlists: Dict[str, List[str]]) -> None:
        """
        Replace playlists state from backend.
        """
        self._playlists = playlists
        self._rebuild()

    def add_track_to_playlist(self, playlist: str, track_id: str) -> None:
        self._playlists.setdefault(playlist, [])
        if track_id not in self._playlists[playlist]:
            self._playlists[playlist].append(track_id)
            self._emit_update(playlist)

    # ------------------------------------------------------------------
    # INTERNAL
    # ------------------------------------------------------------------

    def _rebuild(self) -> None:
        self.list_widget.clear()
        for name in sorted(self._playlists.keys()):
            item = QListWidgetItem(name)
            self.list_widget.addItem(item)

    def _create_playlist(self) -> None:
        name, ok = QInputDialog.getText(self, "New Playlist", "Playlist name")
        if ok and name:
            self._playlists[name] = []
            self._emit_update(name)
            self._rebuild()

    def _rename_playlist(self) -> None:
        if not self._current_playlist:
            return

        name, ok = QInputDialog.getText(
            self,
            "Rename Playlist",
            "New name",
            text=self._current_playlist,
        )
        if ok and name:
            self._playlists[name] = self._playlists.pop(self._current_playlist)
            self._current_playlist = name
            self._emit_update(name)
            self._rebuild()

    def _delete_playlist(self) -> None:
        if not self._current_playlist:
            return

        self._playlists.pop(self._current_playlist, None)
        self._emit_update(self._current_playlist)
        self._current_playlist = None
        self._rebuild()

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        self._current_playlist = item.text()
        self.playlist_selected.emit(self._current_playlist)
        self._signals.playlist_selected.emit(self._current_playlist)

    def _emit_update(self, playlist: str) -> None:
        payload = {
            "playlist": playlist,
            "tracks": self._playlists.get(playlist, []),
        }
        self.playlist_updated.emit(payload)
        self._signals.playlist_updated.emit(payload)
