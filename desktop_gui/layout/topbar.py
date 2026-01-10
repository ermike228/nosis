"""
NOSIS Desktop GUI – TopBar (Save / Mode / Credits)
================================================

Enterprise-grade top command bar (2025–2026).

Responsibilities:
- Global project actions (Save / Load)
- Mode switching (Simple / Pro / Enterprise)
- Credits & quota visibility
- User status & plan indicator
- Global app state feedback

NO business logic
NO backend calls
All actions emitted via signals
"""

from __future__ import annotations

import logging
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from desktop_gui.core.signals import get_signals
from desktop_gui.core.app_state import get_app_state
from desktop_gui.core.permissions import get_permissions

logger = logging.getLogger("nosis.topbar")


# =============================================================================
# TOP BAR
# =============================================================================

class TopBar(QFrame):
    """
    Global application command bar.

    Always visible.
    Stateless UI (driven by AppState + Permissions).
    """

    def __init__(self):
        super().__init__()

        self._signals = get_signals()
        self._state = get_app_state()
        self._permissions = get_permissions()

        self.setObjectName("TopBar")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFixedHeight(56)

        self._init_ui()
        self._connect_signals()

        logger.info("TopBar initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # Left: Project actions
        self.save_btn = TopBarButton("Save")
        self.save_btn.clicked.connect(self._on_save)

        self.save_as_btn = TopBarButton("Save As")
        self.save_as_btn.clicked.connect(self._on_save_as)

        layout.addWidget(self.save_btn)
        layout.addWidget(self.save_as_btn)

        layout.addSpacing(16)

        # Mode indicator / switch
        self.mode_label = QLabel()
        self.mode_label.setObjectName("TopBarMode")
        layout.addWidget(self.mode_label)

        layout.addStretch()

        # Credits
        self.credits_label = QLabel()
        self.credits_label.setObjectName("TopBarCredits")
        layout.addWidget(self.credits_label)

        # User / Plan
        self.user_label = QLabel()
        self.user_label.setObjectName("TopBarUser")
        layout.addWidget(self.user_label)

        self._refresh()

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        self._signals.user_logged_in.connect(self._refresh)
        self._signals.user_logged_out.connect(self._refresh)
        self._signals.credits_updated.connect(self._refresh)
        self._signals.mode_changed.connect(self._refresh)
        self._signals.project_dirty_changed.connect(self._update_dirty_state)

    # ------------------------------------------------------------------
    # STATE
    # ------------------------------------------------------------------

    def _refresh(self, *_):
        """
        Sync UI with AppState.
        """
        user = self._state.user
        mode = self._state.mode
        credits = self._state.credits

        # Mode
        self.mode_label.setText(f"Mode: {mode.capitalize()}")

        # Credits
        if credits is not None:
            self.credits_label.setText(f"Credits: {credits}")
        else:
            self.credits_label.setText("Credits: —")

        # User
        if user.authenticated:
            self.user_label.setText(f"{user.username} · {user.plan.capitalize()}")
        else:
            self.user_label.setText("Not signed in")

        # Permissions
        self.save_btn.setEnabled(self._permissions.can_save_project())
        self.save_as_btn.setEnabled(self._permissions.can_save_project())

    def _update_dirty_state(self, dirty: bool):
        """
        Visual hint when project has unsaved changes.
        """
        suffix = "*" if dirty else ""
        self.save_btn.setText(f"Save{suffix}")

    # ------------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------------

    def _on_save(self):
        self._signals.project_save_requested.emit()

    def _on_save_as(self):
        self._signals.project_save_as_requested.emit()


# =============================================================================
# BUTTON
# =============================================================================

class TopBarButton(QPushButton):
    """
    Styled command button for TopBar.
    """

    def __init__(self, text: str):
        super().__init__(text)
        self.setObjectName("TopBarButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
