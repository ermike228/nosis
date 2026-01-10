"""
NOSIS Desktop GUI – StatusBar (Progress / Errors / System State)
===============================================================

Enterprise-grade status bar (2025–2026).

Responsibilities:
- Global progress indication (generation, uploads, tasks)
- Error & warning surfacing
- Backend connectivity status
- Subtle, non-intrusive UX feedback

Design principles:
- Always visible
- Low visual noise
- Event-driven
- Stateless UI (AppState + Signals)
"""

from __future__ import annotations

import logging
from typing import Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QSizePolicy,
)

from desktop_gui.core.signals import get_signals
from desktop_gui.core.app_state import get_app_state

logger = logging.getLogger("nosis.statusbar")


# =============================================================================
# STATUS BAR
# =============================================================================

class StatusBar(QFrame):
    """
    Global application status bar.

    Shows:
    - progress of long-running operations
    - transient errors / warnings
    - backend connectivity
    """

    AUTO_CLEAR_MESSAGE_MS = 6000

    def __init__(self):
        super().__init__()

        self._signals = get_signals()
        self._state = get_app_state()

        self.setObjectName("StatusBar")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFixedHeight(32)

        self._clear_timer = QTimer(self)
        self._clear_timer.setSingleShot(True)
        self._clear_timer.timeout.connect(self._clear_message)

        self._init_ui()
        self._connect_signals()

        logger.info("StatusBar initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(8)

        # Backend status
        self.backend_status = QLabel("● Offline")
        self.backend_status.setObjectName("StatusBackendOffline")
        layout.addWidget(self.backend_status)

        # Progress
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setVisible(False)
        self.progress.setFixedWidth(180)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)

        # Message
        self.message = QLabel("")
        self.message.setObjectName("StatusMessage")
        self.message.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )
        layout.addWidget(self.message)

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        # Backend connectivity
        self._signals.backend_connected.connect(self._on_backend_connected)
        self._signals.backend_disconnected.connect(self._on_backend_disconnected)

        # Progress
        self._signals.generation_started.connect(self._on_progress_start)
        self._signals.generation_progress.connect(self._on_progress_update)
        self._signals.generation_finished.connect(self._on_progress_finish)
        self._signals.generation_failed.connect(self._on_error)

        # Notifications
        self._signals.notification.connect(self._on_notification)

    # ------------------------------------------------------------------
    # BACKEND STATE
    # ------------------------------------------------------------------

    def _on_backend_connected(self):
        self.backend_status.setText("● Connected")
        self.backend_status.setObjectName("StatusBackendOnline")
        self.backend_status.style().polish(self.backend_status)

    def _on_backend_disconnected(self):
        self.backend_status.setText("● Offline")
        self.backend_status.setObjectName("StatusBackendOffline")
        self.backend_status.style().polish(self.backend_status)

    # ------------------------------------------------------------------
    # PROGRESS
    # ------------------------------------------------------------------

    def _on_progress_start(self):
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self._set_message("Processing…")

    def _on_progress_update(self, value: float):
        self.progress.setValue(int(value * 100))

    def _on_progress_finish(self, *_):
        self.progress.setValue(100)
        self.progress.setVisible(False)
        self._set_message("Completed", auto_clear=True)

    # ------------------------------------------------------------------
    # ERRORS / MESSAGES
    # ------------------------------------------------------------------

    def _on_error(self, message: str):
        logger.error("StatusBar error: %s", message)
        self.progress.setVisible(False)
        self._set_message(f"Error: {message}", error=True)

    def _on_notification(self, message: str, level: str = "info"):
        """
        Generic notifications from bridge layer.
        """
        error = level in ("error", "warning")
        self._set_message(message, error=error)

    def _set_message(
        self,
        text: str,
        *,
        error: bool = False,
        auto_clear: bool = False,
    ):
        self.message.setText(text)

        if error:
            self.message.setObjectName("StatusMessageError")
        else:
            self.message.setObjectName("StatusMessage")

        self.message.style().polish(self.message)

        self._clear_timer.stop()
        if auto_clear:
            self._clear_timer.start(self.AUTO_CLEAR_MESSAGE_MS)

    def _clear_message(self):
        self.message.setText("")
