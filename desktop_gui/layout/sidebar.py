"""
NOSIS Desktop GUI – Sidebar (Left Navigation)
============================================

Enterprise-grade left navigation panel (2025–2026).

Responsibilities:
- Primary navigation
- Mode-aware menu (Simple / Pro / Enterprise)
- Permission & plan gating
- Event-driven routing
- Scalable to 1000+ actions without UX clutter

NO business logic
NO backend calls
"""

from __future__ import annotations

import logging
from typing import List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
    QWidget,
)

from desktop_gui.core.signals import get_signals
from desktop_gui.core.permissions import get_permissions
from desktop_gui.core.app_state import get_app_state

logger = logging.getLogger("nosis.sidebar")


# =============================================================================
# SIDEBAR
# =============================================================================

class Sidebar(QFrame):
    """
    Main left navigation container.

    Concept:
    - minimal visible surface
    - deep functionality behind routes
    - mode-driven visibility
    """

    def __init__(self):
        super().__init__()

        self._signals = get_signals()
        self._permissions = get_permissions()
        self._state = get_app_state()

        self.setFixedWidth(240)
        self.setObjectName("Sidebar")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._items: List[SidebarItem] = []

        self._init_ui()
        self._connect_signals()

        logger.info("Sidebar initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)

        # Logo
        logo = QLabel("NOSIS")
        logo.setObjectName("SidebarLogo")
        logo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(logo)

        layout.addSpacing(24)

        # Primary navigation
        for route in [
            ("home", "Home"),
            ("create", "Create"),
            ("studio", "Studio"),
            ("chat", "Chat Assistant"),
            ("library", "Library"),
            ("subscription", "Subscription"),
            ("notifications", "Notifications"),
        ]:
            self._add_item(layout, route[0], route[1])

        layout.addStretch()

        # Secondary navigation
        for route in [
            ("learning", "Learning"),
            ("help", "Help"),
            ("jobs", "Jobs"),
        ]:
            self._add_item(layout, route[0], route[1], secondary=True)

    def _add_item(
        self,
        layout: QVBoxLayout,
        route: str,
        label: str,
        secondary: bool = False,
    ) -> None:
        item = SidebarItem(
            route=route,
            label=label,
            secondary=secondary,
        )
        self._items.append(item)
        layout.addWidget(item)

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        self._signals.user_logged_in.connect(self.refresh)
        self._signals.user_logged_out.connect(self.refresh)
        self._signals.permissions_changed.connect(self.refresh)
        self._signals.route_changed.connect(self._highlight_active)

    # ------------------------------------------------------------------
    # STATE
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """
        Re-evaluate visibility and enabled state.
        """
        for item in self._items:
            item.update_permissions()

    def _highlight_active(self, route: str) -> None:
        for item in self._items:
            item.set_active(item.route == route)


# =============================================================================
# SIDEBAR ITEM
# =============================================================================

class SidebarItem(QLabel):
    """
    Single navigation entry.

    Design:
    - acts like a button
    - style-driven (no logic)
    """

    def __init__(
        self,
        route: str,
        label: str,
        secondary: bool = False,
    ):
        super().__init__(label)

        self.route = route
        self.secondary = secondary

        self._signals = get_signals()
        self._permissions = get_permissions()

        self._active = False

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self._apply_style()

    # ------------------------------------------------------------------
    # STYLE
    # ------------------------------------------------------------------

    def _apply_style(self) -> None:
        if self.secondary:
            self.setObjectName("SidebarItemSecondary")
        else:
            self.setObjectName("SidebarItem")

    def set_active(self, active: bool) -> None:
        self._active = active
        self.setProperty("active", active)
        self.style().polish(self)

    # ------------------------------------------------------------------
    # INTERACTION
    # ------------------------------------------------------------------

    def mousePressEvent(self, event) -> None:
        if not self.isEnabled():
            return

        if self._permissions.is_route_allowed(self.route):
            self._signals.route_requested.emit(self.route)

    # ------------------------------------------------------------------
    # PERMISSIONS
    # ------------------------------------------------------------------

    def update_permissions(self) -> None:
        allowed = self._permissions.is_route_allowed(self.route)
        self.setEnabled(allowed)
        self.setVisible(allowed or self.secondary)
