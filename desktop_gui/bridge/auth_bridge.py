"""
NOSIS Desktop GUI – Authentication Bridge
========================================

Enterprise-grade authentication bridge for desktop GUI (2025–2026).

Responsibilities:
- Authentication lifecycle (login / logout / refresh)
- Token storage & renewal
- Sync auth state with AppState
- Emit auth-related UI signals
- Abstract backend auth implementation details

This module:
- Contains NO UI code
- Contains NO backend business logic
- Acts as the single auth authority for the GUI
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional, Dict, Any

from desktop_gui.bridge.api_client import get_api_client
from desktop_gui.core.app_state import get_app_state
from desktop_gui.core.signals import get_signals

logger = logging.getLogger("nosis.auth_bridge")


# =============================================================================
# AUTH BRIDGE
# =============================================================================

class AuthBridge:
    """
    Central authentication controller for the desktop application.

    Design goals:
    - Async-first
    - Backend-agnostic (JWT / OAuth / SSO)
    - Stateless UI (all state lives in AppState)
    - Safe token refresh
    """

    def __init__(self):
        self._api = get_api_client()
        self._state = get_app_state()
        self._signals = get_signals()

        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None

        self._refresh_task: Optional[asyncio.Task] = None

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    async def login(self, username: str, password: str) -> None:
        """
        Authenticate user with backend.
        """
        logger.info("Attempting login for user: %s", username)

        response = await self._api._request(
            "POST",
            "/auth/login",
            json={
                "username": username,
                "password": password,
            },
        )

        self._apply_auth_response(response)

        self._signals.user_logged_in.emit(response.get("user", {}))
        logger.info("User logged in successfully")

    async def logout(self) -> None:
        """
        Logout user and clear auth state.
        """
        logger.info("Logging out user")

        try:
            await self._api._request("POST", "/auth/logout")
        except Exception:
            # backend logout failure should not block local logout
            pass

        self._clear_auth_state()
        self._signals.user_logged_out.emit()
        logger.info("User logged out")

    async def restore_session(self) -> bool:
        """
        Attempt to restore existing session (e.g. from OS keychain).

        Returns:
            bool: whether session was restored
        """
        logger.info("Attempting session restore")

        # In a real implementation, tokens would be loaded from
        # OS keychain / encrypted storage.
        if not self._access_token:
            return False

        try:
            response = await self._api._request("GET", "/auth/me")
            self._state.set_user(
                authenticated=True,
                username=response.get("username"),
                plan=response.get("plan", "free"),
            )
            self._signals.user_logged_in.emit(response)
            return True

        except Exception:
            self._clear_auth_state()
            return False

    # ------------------------------------------------------------------
    # TOKEN MANAGEMENT
    # ------------------------------------------------------------------

    def _apply_auth_response(self, response: Dict[str, Any]) -> None:
        """
        Apply authentication response from backend.
        """
        self._access_token = response.get("access_token")
        self._refresh_token = response.get("refresh_token")

        user = response.get("user", {})

        self._state.set_user(
            authenticated=True,
            username=user.get("username"),
            plan=user.get("plan", "free"),
        )

        self._start_token_refresh_loop()

    def _clear_auth_state(self) -> None:
        """
        Clear local auth state.
        """
        self._access_token = None
        self._refresh_token = None

        if self._refresh_task:
            self._refresh_task.cancel()
            self._refresh_task = None

        self._state.set_user(
            authenticated=False,
            username=None,
            plan="free",
        )

    # ------------------------------------------------------------------
    # TOKEN REFRESH
    # ------------------------------------------------------------------

    def _start_token_refresh_loop(self) -> None:
        """
        Start background token refresh loop.
        """
        if self._refresh_task:
            return

        self._refresh_task = asyncio.create_task(self._refresh_loop())

    async def _refresh_loop(self) -> None:
        """
        Periodically refresh access token.
        """
        try:
            while True:
                await asyncio.sleep(60 * 10)  # refresh every 10 minutes

                if not self._refresh_token:
                    return

                logger.debug("Refreshing access token")

                response = await self._api._request(
                    "POST",
                    "/auth/refresh",
                    json={"refresh_token": self._refresh_token},
                )

                self._access_token = response.get("access_token")
                logger.info("Access token refreshed")

        except asyncio.CancelledError:
            return

        except Exception as exc:
            logger.warning("Token refresh failed: %s", exc)
            self._signals.user_logged_out.emit()
            self._clear_auth_state()

    # ------------------------------------------------------------------
    # HEADERS INTEGRATION
    # ------------------------------------------------------------------

    def inject_auth_header(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Inject Authorization header into API requests.
        """
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        return headers


# =============================================================================
# GLOBAL SINGLETON ACCESSOR
# =============================================================================

_auth_bridge: Optional[AuthBridge] = None


def get_auth_bridge() -> AuthBridge:
    """
    Global accessor for AuthBridge.

    Ensures:
    - single auth controller
    - consistent user state
    """
    global _auth_bridge
    if _auth_bridge is None:
        _auth_bridge = AuthBridge()
    return _auth_bridge
