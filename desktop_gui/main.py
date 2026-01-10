#!/usr/bin/env python3
"""
NOSIS Desktop GUI Entrypoint
Enterprise-grade PyQt6 application bootstrap (2026)

Responsibilities:
- Initialize QApplication
- Apply global configuration (theme, fonts, DPI, style)
- Setup async event loop compatibility
- Initialize telemetry & logging hooks
- Instantiate MainWindow
- Provide safe startup & shutdown lifecycle
"""

from __future__ import annotations

import sys
import os
import signal
import logging
from pathlib import Path
from typing import Optional

# --- Qt imports ---
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt

# --- Async / event loop integration ---
import qasync

# --- Optional theming ---
import qdarktheme

# --- Internal imports (no circular dependencies) ---
from layout.main_window import MainWindow

# =============================================================================
# GLOBAL PATHS & CONSTANTS
# =============================================================================

APP_NAME = "NOSIS"
APP_ORG = "NOSIS AI"
APP_VERSION = "0.1.0-dev"

ROOT_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT_DIR / "desktop_gui" / "assets"
LOG_DIR = ROOT_DIR / "logs" / "desktop_gui"

LOG_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# LOGGING (enterprise-level, safe by default)
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "gui.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("nosis.gui")

# =============================================================================
# SAFETY & ENVIRONMENT GUARDS
# =============================================================================

def _ensure_correct_environment() -> None:
    """
    Defensive checks to avoid subtle runtime issues.
    """
    if sys.version_info < (3, 10):
        raise RuntimeError("Python 3.10+ is required for NOSIS Desktop GUI")

    # Prevent Qt from silently misbehaving on HiDPI screens
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
    os.environ.setdefault("QT_SCALE_FACTOR_ROUNDING_POLICY", "PassThrough")

# =============================================================================
# APPLICATION FACTORY
# =============================================================================

def create_application(argv: list[str]) -> QApplication:
    """
    Create and configure QApplication in a controlled, testable way.
    """
    _ensure_correct_environment()

    app = QApplication(argv)

    # --- Application metadata ---
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_ORG)
    app.setApplicationVersion(APP_VERSION)

    # --- High DPI / rendering flags ---
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    # --- Global font (Inter, fallback-safe) ---
    font = QFont("Inter")
    font.setPointSize(10)
    app.setFont(font)

    # --- Theme (Fluent-like base, overridable later) ---
    try:
        qdarktheme.setup_theme(
            theme="dark",
            custom_colors={
                "primary": "#2563EB",   # Microsoft-like blue
            },
        )
        logger.info("Dark theme applied (qdarktheme)")
    except Exception as exc:
        logger.warning("Failed to apply theme: %s", exc)

    # --- App icon (optional but enterprise-standard) ---
    icon_path = ASSETS_DIR / "icons" / "nosis.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    return app

# =============================================================================
# MAIN ENTRYPOINT
# =============================================================================

def main() -> int:
    """
    Main GUI entrypoint.
    This function is intentionally minimal, explicit, and testable.
    """
    logger.info("Starting NOSIS Desktop GUI")

    # --- Async-compatible Qt event loop ---
    app = create_application(sys.argv)
    loop = qasync.QEventLoop(app)
    qasync.asyncio.set_event_loop(loop)

    # --- Graceful shutdown handling ---
    def _graceful_exit(*_):
        logger.info("Graceful shutdown requested")
        app.quit()

    signal.signal(signal.SIGINT, _graceful_exit)
    signal.signal(signal.SIGTERM, _graceful_exit)

    # --- Main window ---
    main_window: Optional[MainWindow] = None

    try:
        main_window = MainWindow()
        main_window.show()

        logger.info("Main window shown successfully")

        # --- Run event loop ---
        with loop:
            exit_code = loop.run_forever()

    except Exception:
        logger.exception("Fatal error during GUI startup")
        exit_code = 1

    finally:
        logger.info("NOSIS Desktop GUI terminated")

    return exit_code

# =============================================================================
# SCRIPT GUARD
# =============================================================================

if __name__ == "__main__":
    sys.exit(main())
