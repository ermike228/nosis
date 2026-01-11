"""
NOSIS Desktop GUI – Permissions, Plans & Limits
==============================================

Enterprise-grade permission & quota engine for UI layer (2025–2026).

Responsibilities:
- Enforce subscription plans (free / pro / enterprise)
- Control access to pages, features, and actions
- Track credits, quotas, and usage limits
- Provide a single source of truth for UI-level permissions

This module contains:
- NO billing logic
- NO backend enforcement
- NO payment integrations

It is a *frontend control plane* that mirrors backend rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from desktop_gui.core.app_state import get_app_state

# =============================================================================
# PLANS
# =============================================================================

PLAN_FREE = "free"
PLAN_PRO = "pro"
PLAN_ENTERPRISE = "enterprise"


# =============================================================================
# PLAN DEFINITIONS
# =============================================================================

@dataclass(frozen=True)
class PlanLimits:
    """
    Immutable definition of plan limits and capabilities.

    These limits are enforced at UI level to:
    - guide UX
    - prevent invalid actions
    - reduce backend error handling
    """

    # Credits / usage
    monthly_credits: int
    max_tracks_per_generation: int

    # Feature access
    studio_access: bool
    advanced_voice_controls: bool
    advanced_visual_controls: bool
    multi_reference_input: bool
    auto_mastering: bool
    chat_assistant: bool

    # Library / export
    max_library_items: int
    export_stems: bool
    commercial_use: bool


# =============================================================================
# PLAN REGISTRY
# =============================================================================

PLAN_REGISTRY: Dict[str, PlanLimits] = {
    PLAN_FREE: PlanLimits(
        monthly_credits=100,
        max_tracks_per_generation=2,
        studio_access=False,
        advanced_voice_controls=False,
        advanced_visual_controls=False,
        multi_reference_input=False,
        auto_mastering=False,
        chat_assistant=False,
        max_library_items=50,
        export_stems=False,
        commercial_use=False,
    ),
    PLAN_PRO: PlanLimits(
        monthly_credits=2000,
        max_tracks_per_generation=4,
        studio_access=True,
        advanced_voice_controls=True,
        advanced_visual_controls=True,
        multi_reference_input=True,
        auto_mastering=True,
        chat_assistant=True,
        max_library_items=1000,
        export_stems=True,
        commercial_use=True,
    ),
    PLAN_ENTERPRISE: PlanLimits(
        monthly_credits=10_000,
        max_tracks_per_generation=8,
        studio_access=True,
        advanced_voice_controls=True,
        advanced_visual_controls=True,
        multi_reference_input=True,
        auto_mastering=True,
        chat_assistant=True,
        max_library_items=100_000,
        export_stems=True,
        commercial_use=True,
    ),
}


# =============================================================================
# PERMISSION MANAGER
# =============================================================================

class PermissionManager:
    """
    Central permission & quota evaluator for the GUI.

    This class is intentionally:
    - stateless (reads from AppState)
    - synchronous
    - side-effect free

    Widgets ask questions, PermissionManager answers them.
    """

    def __init__(self):
        self._state = get_app_state()

    # ------------------------------------------------------------------
    # USER / PLAN
    # ------------------------------------------------------------------

    @property
    def current_plan(self) -> str:
        return self._state.user.plan

    @property
    def limits(self) -> PlanLimits:
        return PLAN_REGISTRY.get(self.current_plan, PLAN_REGISTRY[PLAN_FREE])

    # ------------------------------------------------------------------
    # PAGE ACCESS
    # ------------------------------------------------------------------

    def can_access_page(self, page_name: str) -> bool:
        """
        Check whether current user can access a given page.
        """
        if page_name == "studio":
            return self.limits.studio_access

        if page_name == "admin":
            return self.current_plan == PLAN_ENTERPRISE

        return True

    def is_route_allowed(self, route: str) -> bool:
        return self.can_access_page(route)

    # ------------------------------------------------------------------
    # FEATURE ACCESS
    # ------------------------------------------------------------------

    def can_use_feature(self, feature_name: str) -> bool:
        """
        Generic feature permission check.
        """
        return bool(getattr(self.limits, feature_name, False))

    def can_generate(self) -> bool:
        return self.has_credits()

    def can_save_project(self) -> bool:
        return self._state.user.authenticated

    def inspector_enabled(self) -> bool:
        return self._state.ui_flags.inspector_visible
    # ------------------------------------------------------------------
    # GENERATION LIMITS
    # ------------------------------------------------------------------

    def max_tracks_allowed(self) -> int:
        return self.limits.max_tracks_per_generation

    def has_credits(self, required: int = 1) -> bool:
        """
        UI-level credit availability check.
        """
        # Backend is authoritative; UI only mirrors
        return self._state.user.authenticated and required <= self.limits.monthly_credits

    # ------------------------------------------------------------------
    # LIBRARY LIMITS
    # ------------------------------------------------------------------

    def can_add_to_library(self, current_count: int) -> bool:
        return current_count < self.limits.max_library_items

    # ------------------------------------------------------------------
    # EXPORT / COMMERCIAL
    # ------------------------------------------------------------------

    def can_export_stems(self) -> bool:
        return self.limits.export_stems

     def is_commercial_use_allowed(self) -> bool:
        return self.limits.commercial_use


_permissions: Optional[PermissionManager] = None

def get_permissions() -> PermissionManager:
    global _permissions
    if _permissions is None:
        _permissions = PermissionManager()
    return _permissions

