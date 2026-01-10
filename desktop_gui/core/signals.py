"""
NOSIS Desktop GUI – Global Signals Bus
====================================

Enterprise-grade Qt signals/event bus for PyQt6 (2025–2026).

Role:
- Central, typed event hub for the entire GUI
- Decouples pages, widgets, workers, and services
- Enables scalable, maintainable, and testable UI architecture

Philosophy:
- Event-driven UI (no widget-to-widget coupling)
- Zero business logic
- Explicit, domain-oriented signals
- Safe singleton lifecycle
"""

from __future__ import annotations

from typing import Optional, Any, Dict
from PyQt6.QtCore import QObject, pyqtSignal


class UISignals(QObject):
    """
    Central UI Event Bus.

    This object acts as the single communication backbone
    for the desktop GUI. Every UI event that is not strictly
    local should pass through this bus.

    Pattern:
        Widget / Worker / Service
                ↓
            UISignals
                ↓
        Widget / Page / Controller

    This design scales to hundreds of UI features without
    turning the codebase into spaghetti.
    """

    # ------------------------------------------------------------------
    # APPLICATION LIFECYCLE
    # ------------------------------------------------------------------
    app_started = pyqtSignal()
    app_ready = pyqtSignal()
    app_shutdown_requested = pyqtSignal()
    app_shutdown_completed = pyqtSignal()

    # ------------------------------------------------------------------
    # ROUTING / NAVIGATION
    # ------------------------------------------------------------------
    navigate = pyqtSignal(str)              # page_name
    navigate_back = pyqtSignal()
    navigate_forward = pyqtSignal()

    # ------------------------------------------------------------------
    # PROJECT / WORKSPACE
    # ------------------------------------------------------------------
    project_created = pyqtSignal(str)       # project_id
    project_loaded = pyqtSignal(str)
    project_saved = pyqtSignal(str)
    project_closed = pyqtSignal()
    project_dirty_changed = pyqtSignal(bool)

    # ------------------------------------------------------------------
    # GENERATION PIPELINE
    # ------------------------------------------------------------------
    generation_requested = pyqtSignal(dict)     # full generation payload
    generation_started = pyqtSignal()
    generation_progress = pyqtSignal(float)     # 0.0 .. 1.0
    generation_preview = pyqtSignal(dict)       # streamed / partial output
    generation_finished = pyqtSignal(dict)      # final result metadata
    generation_failed = pyqtSignal(str)
    generation_cancelled = pyqtSignal()

    # ------------------------------------------------------------------
    # BACKEND / CONNECTIVITY
    # ------------------------------------------------------------------
    backend_connected = pyqtSignal()
    backend_disconnected = pyqtSignal()
    backend_latency_updated = pyqtSignal(int)   # ms
    backend_error = pyqtSignal(str)

    # ------------------------------------------------------------------
    # LIBRARY / ASSETS
    # ------------------------------------------------------------------
    library_updated = pyqtSignal()
    track_added = pyqtSignal(str)
    track_selected = pyqtSignal(str)
    track_deleted = pyqtSignal(str)
    asset_imported = pyqtSignal(str)

    # ------------------------------------------------------------------
    # UI / UX STATE
    # ------------------------------------------------------------------
    theme_changed = pyqtSignal(str)              # dark | light | system
    sidebar_toggled = pyqtSignal(bool)
    inspector_toggled = pyqtSignal(bool)
    fullscreen_toggled = pyqtSignal(bool)
    notification = pyqtSignal(str, Optional[str])  # message, level

    # ------------------------------------------------------------------
    # USER / AUTH / BILLING
    # ------------------------------------------------------------------
    user_logged_in = pyqtSignal(dict)
    user_logged_out = pyqtSignal()
    subscription_changed = pyqtSignal(str)
    permissions_updated = pyqtSignal(dict)

    # ------------------------------------------------------------------
    # SETTINGS
    # ------------------------------------------------------------------
    settings_opened = pyqtSignal()
    settings_changed = pyqtSignal(str, Any)      # key, value
    settings_saved = pyqtSignal()

    # ------------------------------------------------------------------
    # DEBUG / TELEMETRY
    # ------------------------------------------------------------------
    debug_event = pyqtSignal(str, Any)
    performance_event = pyqtSignal(str, Dict)


# ----------------------------------------------------------------------
# GLOBAL SINGLETON ACCESSOR
# ----------------------------------------------------------------------

_signals: Optional[UISignals] = None


def get_signals() -> UISignals:
    """
    Global accessor for UISignals.

    Guarantees:
    - exactly one event bus per application
    - predictable signal routing
    - easy mocking for tests
    """
    global _signals
    if _signals is None:
        _signals = UISignals()
    return _signals
