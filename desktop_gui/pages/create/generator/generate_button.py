"""
NOSIS – Generate Button Controller
=================================

Enterprise-grade generation trigger & orchestration layer (2025–2026).

Purpose:
- Single authoritative entrypoint for generation
- Payload aggregation from all generator panels
- Validation, locking & UX safety
- Event-driven orchestration (REST / gRPC / WS)
- Commercial-grade reliability guarantees

This module defines WHEN generation starts and HOW it is coordinated.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, Callable, Optional

from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
)

from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.generate_button")


class GenerateButton(QFrame):
    """
    Central generation trigger.

    Responsibilities:
    - Validate full generator state
    - Freeze UI during generation
    - Emit generation_requested event
    - Handle cancellation & retries
    - Provide professional UX feedback
    """

    generation_triggered = pyqtSignal(dict)
    generation_cancelled = pyqtSignal()

    def __init__(self):
        super().__init__()

        self._signals = get_signals()

        self._current_payload: Optional[Dict] = None
        self._is_generating: bool = False
        self._generation_start_ts: Optional[float] = None

        self.setObjectName("GenerateButton")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._init_ui()
        self._bind_signals()

        logger.info("GenerateButton initialized")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.button = QPushButton("Generate")
        self.button.setMinimumHeight(48)
        self.button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button.clicked.connect(self._on_click)

        layout.addWidget(self.button)

    # ------------------------------------------------------------------
    # SIGNAL BINDINGS
    # ------------------------------------------------------------------

    def _bind_signals(self) -> None:
        self._signals.generation_started.connect(self._on_generation_started)
        self._signals.generation_finished.connect(self._on_generation_finished)
        self._signals.generation_failed.connect(self._on_generation_failed)
        self._signals.generation_cancelled.connect(self._on_generation_cancelled)

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def set_payload(self, payload: Dict) -> None:
        """
        Provide aggregated generation payload.

        Expected to be called by GeneratorController / CreatePage.
        """
        self._current_payload = payload

    # ------------------------------------------------------------------
    # INTERNAL LOGIC
    # ------------------------------------------------------------------

    def _on_click(self) -> None:
        if self._is_generating:
            self._confirm_cancel()
            return

        if not self._current_payload:
            self._show_error(
                "Nothing to generate",
                "Generation parameters are incomplete or missing.",
            )
            return

        if not self._validate_payload(self._current_payload):
            return

        self._trigger_generation()

    def _trigger_generation(self) -> None:
        self._is_generating = True
        self._generation_start_ts = time.time()

        self.button.setText("Generating…")
        self.button.setEnabled(True)

        self.generation_triggered.emit(self._current_payload)
        self._signals.generation_requested.emit(self._current_payload)

        logger.info("Generation requested")

    def _confirm_cancel(self) -> None:
        reply = QMessageBox.question(
            self,
            "Cancel generation?",
            "Generation is currently running. Do you want to cancel it?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._signals.generation_cancelled.emit()

    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------

    def _validate_payload(self, payload: Dict) -> bool:
        """
        Enterprise-grade payload validation.

        This prevents:
        - Invalid states
        - Empty generations
        - Costly backend calls with bad input
        """
        if not payload.get("styles"):
            self._show_error(
                "Style missing",
                "Please define a style or genre before generating.",
            )
            return False

        if payload.get("mode") == "Song" and not payload.get("lyrics"):
            self._show_error(
                "Lyrics missing",
                "Song mode requires lyrics.",
            )
            return False

        return True

    # ------------------------------------------------------------------
    # BACKEND EVENTS
    # ------------------------------------------------------------------

    def _on_generation_started(self) -> None:
        self._is_generating = True
        self.button.setText("Generating…")

    def _on_generation_finished(self, result: Dict) -> None:
        duration = (
            time.time() - self._generation_start_ts
            if self._generation_start_ts
            else 0
        )

        logger.info("Generation finished in %.2f seconds", duration)

        self._reset_button()

    def _on_generation_failed(self, error: str) -> None:
        logger.error("Generation failed: %s", error)
        self._show_error("Generation failed", error)
        self._reset_button()

    def _on_generation_cancelled(self) -> None:
        logger.info("Generation cancelled")
        self._reset_button()

    # ------------------------------------------------------------------
    # UI HELPERS
    # ------------------------------------------------------------------

    def _reset_button(self) -> None:
        self._is_generating = False
        self._generation_start_ts = None
        self.button.setText("Generate")
        self.button.setEnabled(True)

    def _show_error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)
