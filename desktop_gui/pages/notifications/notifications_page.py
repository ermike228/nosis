"""
NOSIS – Notifications Page
=========================

Enterprise-grade Notifications Center for NOSIS (2025–2026).

This module implements a unified, event-driven notification system
covering AI generation, Studio rendering, exports, subscriptions,
system alerts and audit-level messages.

NotificationsPage is NOT a passive feed.
It is an operational control surface for asynchronous workflows.
"""

from __future__ import annotations

import logging
from typing import Dict, List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QComboBox,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.notifications")


class NotificationsPage(QWidget):
    """
    Central notification hub.

    Responsibilities:
    - Display system, AI, Studio and billing notifications
    - Provide filtering and acknowledgement
    - Act as async bridge between backend processes and user
    - Preserve notification history for audit and UX continuity
    """

    notification_selected = pyqtSignal(dict)
    notification_cleared = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()
        self._notifications: List[Dict] = []

        self.setObjectName("NotificationsPage")

        self._init_ui()
        self._bind_signals()

        logger.info("NotificationsPage initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        # --------------------------------------------------------------
        # HEADER
        # --------------------------------------------------------------

        header = QHBoxLayout()

        title = QLabel("Notifications")
        title.setObjectName("NotificationsTitle")

        self.filter_box = QComboBox()
        self.filter_box.addItems([
            "All",
            "AI",
            "Studio",
            "Exports",
            "System",
            "Billing",
        ])
        self.filter_box.currentTextChanged.connect(self._apply_filter)

        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self._clear_all)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.filter_box)
        header.addWidget(clear_btn)

        root.addLayout(header)

        # --------------------------------------------------------------
        # LIST
        # --------------------------------------------------------------

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_clicked)

        root.addWidget(self.list_widget)

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _bind_signals(self) -> None:
        self._signals.notification_received.connect(self.add_notification)

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def add_notification(self, notification: Dict) -> None:
        """
        Add a notification from backend or internal systems.

        Expected payload:
        {
            "id": str,
            "type": "AI|Studio|Exports|System|Billing",
            "title": str,
            "message": str,
            "severity": "info|warning|error",
            "timestamp": str
        }
        """
        self._notifications.append(notification)
        self._render_notification(notification)

    # ------------------------------------------------------------------
    # INTERNAL
    # ------------------------------------------------------------------

    def _render_notification(self, notification: Dict) -> None:
        item = QListWidgetItem()

        text = f"[{notification.get('type')}] {notification.get('title')}"
        item.setText(text)
        item.setData(Qt.ItemDataRole.UserRole, notification)

        self.list_widget.addItem(item)

    def _apply_filter(self, category: str) -> None:
        self.list_widget.clear()

        for n in self._notifications:
            if category == "All" or n.get("type") == category:
                self._render_notification(n)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        notification = item.data(Qt.ItemDataRole.UserRole)
        self.notification_selected.emit(notification)

    def _clear_all(self) -> None:
        self._notifications.clear()
        self.list_widget.clear()
        self.notification_cleared.emit("all")
        self._signals.notifications_cleared.emit("all")
