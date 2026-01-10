"""
NOSIS Desktop Application Bootstrap
----------------------------------

This module encapsulates QApplication lifecycle, global configuration,
and application-wide services initialization.

Architectural role:
- Single source of truth for QApplication
- Safe bootstrap for GUI
- Decouples entrypoint (main.py) from app configuration
- Enables testing, embedding, and future extensibility

Enterprise-grade design (2026)
"""

from __future__ import annotations

import os
import sys
import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QCoreApplication

import qasync

# =============================================================================
# CONSTANTS & PATHS
# =============================================================================

APP_NAME = "NOSIS"
APP_ORG = "NOSIS AI"
APP_DOMAIN = "nosis.ai"
APP_VERSION = "0.1.0-dev"

ROOT_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT_DIR / "desktop_gui" / "assets"
LOG_DIR = ROOT_DIR / "logs" / "desktop_gui"

LOG_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

_logger: Optional[logging.Logger] = None


def get_logger() -> logging.Logger:
    global _logger
    if _logger is None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            handlers=[
                logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        _logger = logging.getLogger("nosis.app")
    return _logger


logger = get_logger()

# =============================================================================
# ENVIRONMENT & RUNTIME SAFETY
# =============================================================================

def configure_runtime_environment() -> None:
    """
    Configure environment variables and runtime flags
    BEFORE QApplication is instantiated.
    """
    if sys.version_info < (3, 10):
        raise RuntimeError("NOSIS Desktop requires Python 3.10+")

    # Qt / HiDPI safety
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
    os.environ.setdefault(
        "QT_SCALE_FACTOR_ROUNDING_POLICY",
        "PassThrough",
    )

    # Prevent Qt plugin path issues in complex environments
    os.environ.setdefault("QT_ASSUME_STDERR_HAS_CONSOLE", "1")

# =============================================================================
# APPLICATION CLASS
# =============================================================================

class NosisApplication(QApplication):
    """
    Central application object for NOSIS Desktop.

    Why subclass QApplication?
    - Centralized lifecycle control
    - Single place for global services
    - Future-proof (telemetry, permissions, plugins)
    """

    def __init__(self, argv: list[str]):
        configure_runtime_environment()
        super().__init__(argv)

        self._async_loop: Optional[qasync.QEventLoop] = None

        self._configure_metadata()
        self._configure_ui_defaults()
        self._configure_icon()

        logger.info("NosisApplication initialized")

    # ---------------------------------------------------------------------

    def _configure_metadata(self) -> None:
        QCoreApplication.setApplicationName(APP_NAME)
        QCoreApplication.setOrganizationName(APP_ORG)
        QCoreApplication.setOrganizationDomain(APP_DOMAIN)
        QCoreApplication.setApplicationVersion(APP_VERSION)

    # ---------------------------------------------------------------------

    def _configure_ui_defaults(self) -> None:
        self.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

        font = QFont("Inter")
        font.setPointSize(10)
        self.setFont(font)

    # ---------------------------------------------------------------------

    def _configure_icon(self) -> None:
        icon_path = ASSETS_DIR / "icons" / "nosis.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        else:
            logger.warning("Application icon not found: %s", icon_path)

    # ---------------------------------------------------------------------
    # ASYNC INTEGRATION
    # ---------------------------------------------------------------------

    def setup_asyncio(self) -> qasync.QEventLoop:
        """
        Attach asyncio-compatible event loop to Qt.

        This enables:
        - async REST calls
        - WebSocket streaming
        - gRPC async clients
        - non-blocking UX
        """
        if self._async_loop is None:
            self._async_loop = qasync.QEventLoop(self)
            qasync.asyncio.set_event_loop(self._async_loop)
            logger.info("Asyncio event loop integrated with Qt")
        return self._async_loop

    # ---------------------------------------------------------------------

    def run(self) -> int:
        """
        Run the application event loop safely.
        """
        loop = self.setup_asyncio()
        logger.info("NOSIS Desktop event loop started")

        with loop:
            return loop.run_forever()

# =============================================================================
# APPLICATION FACTORY
# =============================================================================

_app_instance: Optional[NosisApplication] = None


def get_application(argv: Optional[list[str]] = None) -> NosisApplication:
    """
    Application factory / singleton accessor.

    Ensures:
    - only one QApplication exists
    - safe reuse in tests or embedded contexts
    """
    global _app_instance

    if _app_instance is None:
        if argv is None:
            argv = sys.argv
        _app_instance = NosisApplication(argv)
        logger.info("Global application instance created")

    return _app_instance
