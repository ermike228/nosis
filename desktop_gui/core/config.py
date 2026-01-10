"""
NOSIS Desktop GUI – UI Configuration & Feature Flags
===================================================

Enterprise-grade UI configuration layer (2025–2026).

Purpose:
- Centralized UI feature flags
- UI modes (simple / pro / enterprise)
- Page enablement / disablement
- Future-proof UX experimentation (A/B, staged rollout)

This module intentionally contains:
- NO UI logic
- NO business logic
- NO backend logic

It is a declarative control plane for the GUI.
"""

from __future__ import annotations

from typing import Dict, Set, Any
from dataclasses import dataclass, field


# =============================================================================
# UI MODES
# =============================================================================

UI_MODE_SIMPLE = "simple"
UI_MODE_PRO = "pro"
UI_MODE_ENTERPRISE = "enterprise"


# =============================================================================
# FEATURE FLAGS
# =============================================================================

@dataclass(frozen=True)
class FeatureFlags:
    """
    Immutable feature flags snapshot.

    Feature flags control *visibility* and *availability*
    of UI capabilities without changing code.
    """

    # Core
    generation: bool = True
    library: bool = True
    studio: bool = False
    chat_assistant: bool = False

    # Advanced creation
    advanced_voice_controls: bool = False
    advanced_visual_controls: bool = False
    multi_reference_input: bool = False
    auto_mastering: bool = True

    # UX / power features
    prompt_history: bool = True
    negative_prompt: bool = True
    seed_control: bool = False
    live_preview: bool = False

    # Enterprise / admin
    analytics_panel: bool = False
    admin_pages: bool = False
    billing_ui: bool = True


# =============================================================================
# PAGE REGISTRY
# =============================================================================

@dataclass(frozen=True)
class PageConfig:
    """
    Declarative page configuration.

    Router relies on this to decide:
    - which pages exist
    - which pages are enabled
    - which pages are preloaded
    """

    enabled_pages: Set[str] = field(default_factory=set)
    preload_pages: Set[str] = field(default_factory=set)


# =============================================================================
# MAIN UI CONFIG
# =============================================================================

class UIConfig:
    """
    Central UI configuration object.

    This class answers questions like:
    - Is page X enabled?
    - Which pages should be preloaded?
    - Which features are available in current mode?

    It is intentionally lightweight and side-effect free.
    """

    def __init__(self, mode: str = UI_MODE_SIMPLE):
        self._mode = mode

        self._flags = self._resolve_feature_flags(mode)
        self._pages = self._resolve_pages(mode)

    # ------------------------------------------------------------------
    # MODE
    # ------------------------------------------------------------------

    @property
    def mode(self) -> str:
        return self._mode

    # ------------------------------------------------------------------
    # FEATURE FLAGS
    # ------------------------------------------------------------------

    @property
    def flags(self) -> FeatureFlags:
        return self._flags

    def is_feature_enabled(self, name: str) -> bool:
        return bool(getattr(self._flags, name, False))

    # ------------------------------------------------------------------
    # PAGES
    # ------------------------------------------------------------------

    @property
    def enabled_pages(self) -> Set[str]:
        return self._pages.enabled_pages

    @property
    def preload_pages(self) -> Set[str]:
        return self._pages.preload_pages

    def is_page_enabled(self, page_name: str) -> bool:
        return page_name in self._pages.enabled_pages

    # ------------------------------------------------------------------
    # INTERNAL RESOLUTION
    # ------------------------------------------------------------------

    def _resolve_feature_flags(self, mode: str) -> FeatureFlags:
        """
        Resolve feature flags based on UI mode.
        """
        if mode == UI_MODE_SIMPLE:
            return FeatureFlags(
                studio=False,
                chat_assistant=False,
                advanced_voice_controls=False,
                advanced_visual_controls=False,
                multi_reference_input=False,
                seed_control=False,
                live_preview=False,
                analytics_panel=False,
                admin_pages=False,
            )

        if mode == UI_MODE_PRO:
            return FeatureFlags(
                studio=True,
                chat_assistant=True,
                advanced_voice_controls=True,
                advanced_visual_controls=True,
                multi_reference_input=True,
                seed_control=True,
                live_preview=True,
                analytics_panel=False,
                admin_pages=False,
            )

        if mode == UI_MODE_ENTERPRISE:
            return FeatureFlags(
                studio=True,
                chat_assistant=True,
                advanced_voice_controls=True,
                advanced_visual_controls=True,
                multi_reference_input=True,
                seed_control=True,
                live_preview=True,
                analytics_panel=True,
                admin_pages=True,
                billing_ui=True,
            )

        # Fallback safety
        return FeatureFlags()

    def _resolve_pages(self, mode: str) -> PageConfig:
        """
        Resolve page availability & preload strategy.
        """
        if mode == UI_MODE_SIMPLE:
            return PageConfig(
                enabled_pages={
                    "home",
                    "create",
                    "library",
                    "subscription",
                    "help",
                },
                preload_pages={
                    "home",
                    "create",
                },
            )

        if mode == UI_MODE_PRO:
            return PageConfig(
                enabled_pages={
                    "home",
                    "create",
                    "studio",
                    "library",
                    "chat",
                    "notifications",
                    "subscription",
                    "learning",
                    "help",
                },
                preload_pages={
                    "home",
                    "create",
                    "library",
                },
            )

        if mode == UI_MODE_ENTERPRISE:
            return PageConfig(
                enabled_pages={
                    "home",
                    "create",
                    "studio",
                    "library",
                    "chat",
                    "notifications",
                    "subscription",
                    "learning",
                    "admin",
                    "jobs",
                    "help",
                },
                preload_pages={
                    "home",
                    "create",
                    "studio",
                    "library",
                },
            )

        return PageConfig()
