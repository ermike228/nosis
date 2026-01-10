"""
NOSIS Desktop GUI – Main Window
==============================

Enterprise-grade main application window (2025–2026).

Layout:
--------------------------------------------------
| Sidebar |        Workspace        | Inspector  |
--------------------------------------------------

Responsibilities:
- Root UI composition
- Layout orchestration
- Signal wiring (UI <-> AppState)
- Page routing integration
- Global shortcuts & lifecycle
"""

from __future__ import annotations

import logging
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
    QFrame,
)

from desktop_gui.core.router import get_router
from desktop_gui.core.signals import get_signals
from desktop_gui.core.app_state import get_app_state
from desktop_gui.core.permissions import get_permissions

logger = logging.getLogger("nosis.main_window")


# =============================================================================
# MAIN WINDOW
# =============================================================================

class MainWindow(QMainWindow):
    """
    Root window of the NOSIS desktop application.

    This class is intentionally:
    - layout-focused
    - orchestration-only
    - free from business logic

    All behavior is delegated via:
    - router
    - signals
    - app_state
    """

    def __init__(self):
        super().__init__()

        self._state = get_app_state()
        self._signals = get_signals()
        self._router = get_router()
        self._permissions = get_permissions()

        self._init_window()
        self._init_layout()
        self._connect_signals()

        logger.info("MainWindow initialized")

    # ------------------------------------------------------------------
    # WINDOW CONFIG
    # ------------------------------------------------------------------

    def _init_window(self) -> None:
        self.setWindowTitle("NOSIS")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setUnifiedTitleAndToolBarOnMac(True)

    # ------------------------------------------------------------------
    # LAYOUT
    # ------------------------------------------------------------------

    def _init_layout(self) -> None:
        """
        Compose root layout:
        Sidebar | Workspace | Inspector
        """
        root = QWidget(self)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        root_layout.addWidget(self.sidebar)

        # Workspace (router-controlled)
        self.workspace = Workspace(self._router)
        root_layout.addWidget(self.workspace, stretch=1)

        # Inspector
        self.inspector = Inspector()
        root_layout.addWidget(self.inspector)

        self.setCentralWidget(root)

    # ------------------------------------------------------------------
    # SIGNAL WIRING
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        """
        Bind application-wide signals.
        """
        self._signals.route_changed.connect(self._on_route_changed)
        self._signals.user_logged_in.connect(self._on_user_changed)
        self._signals.user_logged_out.connect(self._on_user_changed)
        self._signals.selection_changed.connect(self.inspector.update_content)

    # ------------------------------------------------------------------
    # HANDLERS
    # ------------------------------------------------------------------

    def _on_route_changed(self, route: str) -> None:
        logger.debug("Route changed: %s", route)
        self.workspace.set_page(route)

    def _on_user_changed(self, *_):
        """
        Update UI when user / plan changes.
        """
        self.sidebar.refresh_permissions()
        self.inspector.refresh_permissions()


# =============================================================================
# SIDEBAR
# =============================================================================

class Sidebar(QFrame):
    """
    Left navigation panel.
    """

    def __init__(self):
        super().__init__()
        self._permissions = get_permissions()
        self._signals = get_signals()

        self.setFixedWidth(240)
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self.logo = QLabel("NOSIS")
        self.logo.setObjectName("SidebarLogo")
        layout.addWidget(self.logo)

        layout.addSpacing(24)

        self.nav_items = []
        for route in [
            "home",
            "create",
            "studio",
            "library",
            "chat",
            "subscription",
            "notifications",
        ]:
            item = SidebarItem(route)
            self.nav_items.append(item)
            layout.addWidget(item)

        layout.addStretch()

        for route in ["learning", "help", "jobs"]:
            item = SidebarItem(route, secondary=True)
            self.nav_items.append(item)
            layout.addWidget(item)

    def refresh_permissions(self) -> None:
        """
        Enable / disable items based on user plan.
        """
        for item in self.nav_items:
            item.update_permissions()


class SidebarItem(QLabel):
    """
    Single clickable navigation item.
    """

    def __init__(self, route: str, secondary: bool = False):
        super().__init__(route.capitalize())

        self.route = route
        self.secondary = secondary
        self._signals = get_signals()
        self._permissions = get_permissions()

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setObjectName("SidebarItemSecondary" if secondary else "SidebarItem")

    def mousePressEvent(self, event):
        if self._permissions.is_route_allowed(self.route):
            self._signals.route_requested.emit(self.route)

    def update_permissions(self) -> None:
        self.setEnabled(self._permissions.is_route_allowed(self.route))


# =============================================================================
# WORKSPACE
# =============================================================================

class Workspace(QFrame):
    """
    Central workspace area controlled by Router.
    """

    def __init__(self, router):
        super().__init__()
        self._router = router

        self.setFrameShape(QFrame.Shape.NoFrame)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(router.widget)

    def set_page(self, route: str) -> None:
        self._router.navigate(route)


# =============================================================================
# INSPECTOR
# =============================================================================

class Inspector(QFrame):
    """
    Right contextual panel (selection-based).
    """

    def __init__(self):
        super().__init__()
        self._permissions = get_permissions()

        self.setFixedWidth(320)
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        self.title = QLabel("Inspector")
        self.title.setObjectName("InspectorTitle")
        layout.addWidget(self.title)

        self.content = QLabel("Select an item")
        self.content.setWordWrap(True)
        layout.addWidget(self.content)

        layout.addStretch()

    def update_content(self, data: Optional[dict]) -> None:
        """
        Update inspector based on current selection.
        """
        if not data:
            self.content.setText("Select an item")
            return

        self.content.setText(str(data))

    def refresh_permissions(self) -> None:
        self.setVisible(self._permissions.inspector_enabled())
