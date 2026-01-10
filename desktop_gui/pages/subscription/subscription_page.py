"""
NOSIS – Subscription Page
========================

Enterprise-grade Subscription & Capability Control Center for NOSIS (2025–2026).

This page is NOT about payments.
It is about dynamic control of product capabilities, limits, and access levels
across the entire NOSIS ecosystem.

SubscriptionPage acts as:
- Feature gatekeeper
- Quota visualizer
- Capability negotiator between UI and backend
"""

from __future__ import annotations

import logging
from typing import Dict

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QPushButton,
    QProgressBar,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.subscription")


class SubscriptionPage(QWidget):
    """
    Subscription & capabilities management page.

    Responsibilities:
    - Display current plan and entitlements
    - Visualize usage vs limits
    - Drive feature gating across UI
    - Act as authoritative UI source for permissions
    """

    upgrade_requested = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self._signals = get_signals()

        self._plan: Dict = {}
        self._usage: Dict = {}

        self.setObjectName("SubscriptionPage")

        self._init_ui()
        self._bind_signals()

        logger.info("SubscriptionPage initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # --------------------------------------------------------------
        # PLAN OVERVIEW
        # --------------------------------------------------------------

        self.plan_box = QGroupBox("Current Plan")
        plan_layout = QVBoxLayout(self.plan_box)

        self.plan_label = QLabel("Plan: Free")
        self.plan_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.upgrade_btn = QPushButton("Upgrade Plan")
        self.upgrade_btn.clicked.connect(self._request_upgrade)

        plan_layout.addWidget(self.plan_label)
        plan_layout.addWidget(self.upgrade_btn)

        root.addWidget(self.plan_box)

        # --------------------------------------------------------------
        # USAGE
        # --------------------------------------------------------------

        self.usage_box = QGroupBox("Usage & Limits")
        usage_layout = QVBoxLayout(self.usage_box)

        self.gen_progress = QProgressBar()
        self.gen_progress.setFormat("Generations: %v / %m")

        self.export_progress = QProgressBar()
        self.export_progress.setFormat("Exports: %v / %m")

        self.studio_progress = QProgressBar()
        self.studio_progress.setFormat("Studio Time: %v / %m")

        usage_layout.addWidget(self.gen_progress)
        usage_layout.addWidget(self.export_progress)
        usage_layout.addWidget(self.studio_progress)

        root.addWidget(self.usage_box)

        # --------------------------------------------------------------
        # FEATURES
        # --------------------------------------------------------------

        self.features_box = QGroupBox("Unlocked Capabilities")
        features_layout = QVBoxLayout(self.features_box)

        self.features_label = QLabel("• Basic Generation• Limited Exports")
        self.features_label.setWordWrap(True)

        features_layout.addWidget(self.features_label)
        root.addWidget(self.features_box)

        root.addStretch()

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _bind_signals(self) -> None:
        self._signals.subscription_updated.connect(self.set_subscription)

    # ------------------------------------------------------------------
    # DATA
    # ------------------------------------------------------------------

    def set_subscription(self, payload: Dict) -> None:
        """
        Update subscription state from backend.

        Expected payload:
        {
            "plan": str,
            "limits": {
                "generations": int,
                "exports": int,
                "studio_minutes": int
            },
            "usage": {
                "generations": int,
                "exports": int,
                "studio_minutes": int
            },
            "features": [str]
        }
        """

        self._plan = payload
        self._usage = payload.get("usage", {})

        self.plan_label.setText(f"Plan: {payload.get('plan', 'Unknown')}")

        limits = payload.get("limits", {})
        usage = payload.get("usage", {})

        self.gen_progress.setMaximum(limits.get("generations", 0))
        self.gen_progress.setValue(usage.get("generations", 0))

        self.export_progress.setMaximum(limits.get("exports", 0))
        self.export_progress.setValue(usage.get("exports", 0))

        self.studio_progress.setMaximum(limits.get("studio_minutes", 0))
        self.studio_progress.setValue(usage.get("studio_minutes", 0))

        features = payload.get("features", [])
        self.features_label.setText("\n".join(f"• {f}" for f in features))

        logger.debug("Subscription updated: %s", payload)

    # ------------------------------------------------------------------
    # INTERNAL
    # ------------------------------------------------------------------

    def _request_upgrade(self) -> None:
        plan = self._plan.get("plan", "Free")
        self.upgrade_requested.emit(plan)
        self._signals.upgrade_requested.emit(plan)
