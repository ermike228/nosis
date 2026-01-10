"""
NOSIS Desktop GUI – Home Page
============================

Enterprise-grade home / dashboard page (2025–2026).

Purpose:
- First screen user sees
- Product orientation & quick actions
- Status overview (account, credits, backend)
- Entry points to core workflows

Design principles:
- Zero clutter
- Action-oriented
- State-driven
- Extensible without refactor
"""

from __future__ import annotations

import logging
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSizePolicy,
)

from desktop_gui.core.app_state import get_app_state
from desktop_gui.core.signals import get_signals
from desktop_gui.core.permissions import get_permissions

logger = logging.getLogger("nosis.home_page")


# =============================================================================
# HOME PAGE
# =============================================================================

class HomePage(QWidget):
    """
    Main landing page of NOSIS.

    This page is:
    - informational
    - navigational
    - never heavy or complex

    All complex functionality lives in Create / Studio / Library.
    """

    ROUTE = "home"

    def __init__(self):
        super().__init__()

        self._state = get_app_state()
        self._signals = get_signals()
        self._permissions = get_permissions()

        self.setObjectName("HomePage")

        self._init_ui()
        self._connect_signals()

        logger.info("HomePage initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 32, 48, 32)
        root.setSpacing(32)

        # ------------------------------------------------------------------
        # HEADER
        # ------------------------------------------------------------------

        header = QLabel("Welcome to NOSIS")
        header.setObjectName("HomeHeader")
        root.addWidget(header)

        subtitle = QLabel(
            "An AI music system that thinks like a composer, producer and engineer."
        )
        subtitle.setObjectName("HomeSubtitle")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        # ------------------------------------------------------------------
        # QUICK ACTIONS
        # ------------------------------------------------------------------

        actions = QHBoxLayout()
        actions.setSpacing(16)

        self.create_btn = PrimaryActionButton(
            "Create Music",
            "Generate a new song or composition",
        )
        self.create_btn.clicked.connect(
            lambda: self._signals.route_requested.emit("create")
        )

        self.studio_btn = SecondaryActionButton(
            "Open Studio",
            "Edit, refine and master tracks",
        )
        self.studio_btn.clicked.connect(
            lambda: self._signals.route_requested.emit("studio")
        )

        self.library_btn = SecondaryActionButton(
            "Open Library",
            "Browse generated tracks",
        )
        self.library_btn.clicked.connect(
            lambda: self._signals.route_requested.emit("library")
        )

        actions.addWidget(self.create_btn)
        actions.addWidget(self.studio_btn)
        actions.addWidget(self.library_btn)
        actions.addStretch()

        root.addLayout(actions)

        # ------------------------------------------------------------------
        # STATUS CARDS
        # ------------------------------------------------------------------

        status_row = QHBoxLayout()
        status_row.setSpacing(16)

        self.account_card = StatusCard("Account")
        self.backend_card = StatusCard("System")
        self.credits_card = StatusCard("Credits")

        status_row.addWidget(self.account_card)
        status_row.addWidget(self.backend_card)
        status_row.addWidget(self.credits_card)

        root.addLayout(status_row)
        root.addStretch()

        self._refresh()

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        self._signals.user_logged_in.connect(self._refresh)
        self._signals.user_logged_out.connect(self._refresh)
        self._signals.backend_connected.connect(self._refresh)
        self._signals.backend_disconnected.connect(self._refresh)
        self._signals.credits_updated.connect(self._refresh)

    # ------------------------------------------------------------------
    # STATE
    # ------------------------------------------------------------------

    def _refresh(self, *_):
        """
        Sync UI with AppState.
        """
        user = self._state.user

        # Account
        if user.authenticated:
            self.account_card.set_value(
                f"{user.username}\nPlan: {user.plan.capitalize()}"
            )
        else:
            self.account_card.set_value("Not signed in")

        # Backend
        if self._state.backend_connected:
            self.backend_card.set_value("Connected\nAll systems operational")
        else:
            self.backend_card.set_value("Offline\nCheck backend")

        # Credits
        if self._state.credits is not None:
            self.credits_card.set_value(str(self._state.credits))
        else:
            self.credits_card.set_value("—")

        # Permissions
        self.create_btn.setEnabled(self._permissions.can_generate())


# =============================================================================
# COMPONENTS
# =============================================================================

class StatusCard(QFrame):
    """
    Small informational card.
    """

    def __init__(self, title: str):
        super().__init__()

        self.setObjectName("HomeStatusCard")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self.title = QLabel(title)
        self.title.setObjectName("HomeStatusTitle")
        layout.addWidget(self.title)

        self.value = QLabel("—")
        self.value.setObjectName("HomeStatusValue")
        self.value.setWordWrap(True)
        layout.addWidget(self.value)

    def set_value(self, text: str) -> None:
        self.value.setText(text)


class PrimaryActionButton(QPushButton):
    """
    Large primary call-to-action button.
    """

    def __init__(self, title: str, subtitle: str):
        super().__init__()

        self.setObjectName("HomePrimaryAction")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("HomeActionTitle")

        subtitle_lbl = QLabel(subtitle)
        subtitle_lbl.setObjectName("HomeActionSubtitle")
        subtitle_lbl.setWordWrap(True)

        layout.addWidget(title_lbl)
        layout.addWidget(subtitle_lbl)


class SecondaryActionButton(QPushButton):
    """
    Secondary call-to-action button.
    """

    def __init__(self, title: str, subtitle: str):
        super().__init__()

        self.setObjectName("HomeSecondaryAction")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("HomeActionTitle")

        subtitle_lbl = QLabel(subtitle)
        subtitle_lbl.setObjectName("HomeActionSubtitle")
        subtitle_lbl.setWordWrap(True)

        layout.addWidget(title_lbl)
        layout.addWidget(subtitle_lbl)
