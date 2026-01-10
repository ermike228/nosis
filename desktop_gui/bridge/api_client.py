"""
NOSIS Desktop GUI – API Client (FastAPI / REST)
=============================================

Enterprise-grade API client for desktop GUI (2025–2026).

Responsibilities:
- Typed, resilient communication with FastAPI backend
- Async-first (non-blocking UI)
- Centralized error handling
- Auth / headers / retries / timeouts
- Streaming-ready architecture (future-proof)

This module contains:
- NO UI code
- NO business logic
- NO ML logic

It is the ONLY allowed way for GUI to talk to backend.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional

import httpx

from desktop_gui.core.app_state import get_app_state
from desktop_gui.core.signals import get_signals

# =============================================================================
# CONFIGURATION
# =============================================================================

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_TIMEOUT = 60.0

logger = logging.getLogger("nosis.api_client")

# =============================================================================
# API CLIENT
# =============================================================================

class APIClient:
    """
    Central REST API client for NOSIS Desktop GUI.

    Design goals:
    - One client instance per app
    - Async-only public interface
    - Safe error propagation via signals
    - Backend-agnostic (can swap FastAPI → gRPC later)
    """

    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self._base_url = base_url.rstrip("/")
        self._state = get_app_state()
        self._signals = get_signals()

        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=DEFAULT_TIMEOUT,
        )

    # ------------------------------------------------------------------
    # LOW-LEVEL REQUEST LAYER
    # ------------------------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Unified request handler with:
        - auth headers
        - error handling
        - latency tracking
        """
        url = f"{self._base_url}{path}"

        headers = self._build_headers()

        try:
            response = await self._client.request(
                method=method,
                url=url,
                json=json,
                params=params,
                headers=headers,
            )

            latency_ms = int(response.elapsed.total_seconds() * 1000)
            self._signals.backend_latency_updated.emit(latency_ms)

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as exc:
            logger.error("HTTP error %s: %s", exc.response.status_code, exc)
            self._signals.backend_error.emit(str(exc))
            raise

        except httpx.RequestError as exc:
            logger.error("Backend connection error: %s", exc)
            self._signals.backend_disconnected.emit()
            raise

    # ------------------------------------------------------------------
    # HEADERS / AUTH
    # ------------------------------------------------------------------

    def _build_headers(self) -> Dict[str, str]:
        """
        Build request headers.
        """
        headers = {
            "Content-Type": "application/json",
            "X-Client": "nosis-desktop",
        }

        if self._state.user.authenticated:
            # token handling can be extended later
            headers["Authorization"] = f"Bearer dummy-token"

        return headers

    # ------------------------------------------------------------------
    # HEALTH / CONNECTION
    # ------------------------------------------------------------------

    async def health_check(self) -> bool:
        """
        Check backend availability.
        """
        try:
            await self._request("GET", "/health")
            self._signals.backend_connected.emit()
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # GENERATION API
    # ------------------------------------------------------------------

    async def generate_music(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger music generation.

        Payload example:
        {
            "lyrics": "...",
            "style": "...",
            "voice": "...",
            "options": {...}
        }
        """
        self._signals.generation_started.emit()

        try:
            result = await self._request(
                "POST",
                "/generate/music",
                json=payload,
            )
            self._signals.generation_finished.emit(result)
            return result

        except Exception as exc:
            self._signals.generation_failed.emit(str(exc))
            raise

    # ------------------------------------------------------------------
    # LIBRARY API
    # ------------------------------------------------------------------

    async def fetch_library(self) -> Dict[str, Any]:
        """
        Fetch user's generated tracks.
        """
        return await self._request("GET", "/library")

    async def delete_track(self, track_id: str) -> None:
        """
        Delete a track from library.
        """
        await self._request("DELETE", f"/library/{track_id}")
        self._signals.track_deleted.emit(track_id)

    # ------------------------------------------------------------------
    # PROJECT API
    # ------------------------------------------------------------------

    async def save_project(self, project_data: Dict[str, Any]) -> None:
        await self._request("POST", "/projects/save", json=project_data)

    async def load_project(self, project_id: str) -> Dict[str, Any]:
        return await self._request("GET", f"/projects/{project_id}")

    # ------------------------------------------------------------------
    # SHUTDOWN
    # ------------------------------------------------------------------

    async def close(self) -> None:
        await self._client.aclose()


# =============================================================================
# GLOBAL SINGLETON ACCESSOR
# =============================================================================

_api_client: Optional[APIClient] = None


def get_api_client() -> APIClient:
    """
    Global API client accessor.

    Guarantees:
    - one HTTP client
    - connection reuse
    - consistent headers & behavior
    """
    global _api_client
    if _api_client is None:
        _api_client = APIClient()
    return _api_client
