"""
NOSIS Desktop UI Global State
----------------------------

Enterprise-grade application state container for PyQt6 GUI.

Responsibilities:
- Single source of truth for UI state
- Signal-driven reactivity (Qt-native)
- Decouples widgets from each other
- Supports feature flags, permissions, async updates
- Safe for multi-window & future plugin architecture

Design philosophy:
- Immutable-style updates
- Explicit state domains
- No business logic
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from dataclasses import dataclass, field

from PyQt6.QtCore import QObject, pyqtSignal, QMutex, QMutexLocker


# =============================================================================
# STATE DOMAIN MODELS
# =============================================================================

@dataclass(frozen=True)
class UserState:
    user_id: Optional[str] = None
    username: Optional[str] = None
    plan: str = "free"              # free | pro | enterprise
    authenticated: bool = False


@dataclass(frozen=True)
class ProjectState:
    project_id: Optional[str] = None
    title: str = "Untitled Project"
    dirty: bool = False             # unsaved changes
    mode: str = "simple"            # simple | pro


@dataclass(frozen=True)
class GenerationState:
    in_progress: bool = False
    progress: float = 0.0
    last_error: Optional[str] = None


@dataclass(frozen=True)
class BackendState:
    connected: bool = False
    latency_ms: Optional[int] = None


@dataclass(frozen=True)
class UIFlags:
    dark_mode: bool = True
    sidebar_collapsed: bool = False
    inspector_visible: bool = True


# =============================================================================
# APPLICATION STATE CONTAINER
# =============================================================================

class AppState(QObject):
    """
    Central reactive UI state container.

    This replaces:
    - global variables
    - widget-to-widget calls
    - implicit shared state

    Architecture:
    Widgets ──signals──▶ AppState ──signals──▶ Widgets
    """

    # ---- granular signals (enterprise-level) ----
    user_changed = pyqtSignal(UserState)
    project_changed = pyqtSignal(ProjectState)
    generation_changed = pyqtSignal(GenerationState)
    backend_changed = pyqtSignal(BackendState)
    ui_flags_changed = pyqtSignal(UIFlags)

    # ---- generic signal (debug / telemetry) ----
    state_changed = pyqtSignal(str, object)

    def __init__(self):
        super().__init__()
        self._mutex = QMutex()

        # Internal immutable state snapshots
        self._user = UserState()
        self._project = ProjectState()
        self._generation = GenerationState()
        self._backend = BackendState()
        self._ui_flags = UIFlags()

    # =========================================================================
    # READ-ONLY ACCESSORS (SAFE)
    # =========================================================================

    @property
    def user(self) -> UserState:
        return self._user

    @property
    def project(self) -> ProjectState:
        return self._project

    @property
    def generation(self) -> GenerationState:
        return self._generation

    @property
    def backend(self) -> BackendState:
        return self._backend

    @property
    def ui_flags(self) -> UIFlags:
        return self._ui_flags

    # =========================================================================
    # STATE UPDATE API (IMMUTABLE, SIGNAL-DRIVEN)
    # =========================================================================

    def set_user(self, **kwargs) -> None:
        with QMutexLocker(self._mutex):
            self._user = UserState(**{**self._user.__dict__, **kwargs})
        self.user_changed.emit(self._user)
        self.state_changed.emit("user", self._user)

    def set_project(self, **kwargs) -> None:
        with QMutexLocker(self._mutex):
            self._project = ProjectState(**{**self._project.__dict__, **kwargs})
        self.project_changed.emit(self._project)
        self.state_changed.emit("project", self._project)

    def set_generation(self, **kwargs) -> None:
        with QMutexLocker(self._mutex):
            self._generation = GenerationState(**{**self._generation.__dict__, **kwargs})
        self.generation_changed.emit(self._generation)
        self.state_changed.emit("generation", self._generation)

    def set_backend(self, **kwargs) -> None:
        with QMutexLocker(self._mutex):
            self._backend = BackendState(**{**self._backend.__dict__, **kwargs})
        self.backend_changed.emit(self._backend)
        self.state_changed.emit("backend", self._backend)

    def set_ui_flags(self, **kwargs) -> None:
        with QMutexLocker(self._mutex):
            self._ui_flags = UIFlags(**{**self._ui_flags.__dict__, **kwargs})
        self.ui_flags_changed.emit(self._ui_flags)
        self.state_changed.emit("ui_flags", self._ui_flags)

    # =========================================================================
    # CONVENIENCE / HIGH-LEVEL ACTIONS
    # =========================================================================

    def mark_project_dirty(self) -> None:
        self.set_project(dirty=True)

    def clear_project_dirty(self) -> None:
        self.set_project(dirty=False)

    def start_generation(self) -> None:
        self.set_generation(in_progress=True, progress=0.0, last_error=None)

    def update_generation_progress(self, value: float) -> None:
        self.set_generation(progress=value)

    def finish_generation(self) -> None:
        self.set_generation(in_progress=False, progress=1.0)

    def fail_generation(self, error: str) -> None:
        self.set_generation(in_progress=False, last_error=error)

# =============================================================================
# GLOBAL SINGLETON ACCESSOR
# =============================================================================

_app_state: Optional[AppState] = None


def get_app_state() -> AppState:
    """
    Global AppState accessor.

    Safe singleton:
    - one state per application
    - predictable lifecycle
    """
    global _app_state
    if _app_state is None:
        _app_state = AppState()
    return _app_state
