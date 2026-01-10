"""
NOSIS Desktop GUI – WebSocket Client (Realtime Progress & Events)
================================================================

Enterprise-grade WebSocket client for realtime UI updates (2025–2026).

Purpose:
- Low-latency progress updates
- Live generation status
- Server-pushed events
- Cancellation / heartbeat handling

This module:
- NEVER blocks the UI
- NEVER touches widgets directly
- Uses signals & AppState only
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Optional, Dict, Any

import websockets

from desktop_gui.core.signals import get_signals
from desktop_gui.core.app_state import get_app_state

# =============================================================================
# CONFIGURATION
# =============================================================================

DEFAULT_WS_URL = "ws://127.0.0.1:8000/ws/progress"
HEARTBEAT_INTERVAL = 10.0  # seconds

logger = logging.getLogger("nosis.ws_client")

# =============================================================================
# WEBSOCKET CLIENT
# =============================================================================

class WebSocketClient:
    """
    Async WebSocket client for realtime backend events.

    Design goals:
    - Async-only
    - Automatic reconnect
    - Heartbeat support
    - Clean shutdown
    - Event-driven UI integration
    """

    def __init__(self, url: str = DEFAULT_WS_URL):
        self._url = url
        self._signals = get_signals()
        self._state = get_app_state()

        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._task: Optional[asyncio.Task] = None
        self._running: bool = False

    # ------------------------------------------------------------------
    # LIFECYCLE
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """
        Start WebSocket connection and listener loop.
        """
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._run())
        logger.info("WebSocket client started")

    async def stop(self) -> None:
        """
        Stop WebSocket connection gracefully.
        """
        self._running = False

        if self._task:
            self._task.cancel()

        if self._ws:
            await self._ws.close()

        logger.info("WebSocket client stopped")

    # ------------------------------------------------------------------
    # INTERNAL LOOP
    # ------------------------------------------------------------------

    async def _run(self) -> None:
        """
        Main connection & listen loop with auto-reconnect.
        """
        while self._running:
            try:
                logger.info("Connecting to WebSocket: %s", self._url)
                async with websockets.connect(self._url) as ws:
                    self._ws = ws
                    self._signals.backend_connected.emit()

                    heartbeat = asyncio.create_task(self._heartbeat())

                    async for message in ws:
                        await self._handle_message(message)

                    heartbeat.cancel()

            except asyncio.CancelledError:
                break

            except Exception as exc:
                logger.warning("WebSocket error: %s", exc)
                self._signals.backend_disconnected.emit()
                await asyncio.sleep(2.0)  # reconnect backoff

    # ------------------------------------------------------------------
    # HEARTBEAT
    # ------------------------------------------------------------------

    async def _heartbeat(self) -> None:
        """
        Periodic ping to keep connection alive.
        """
        while self._running and self._ws:
            try:
                await self._ws.send(json.dumps({"type": "ping"}))
                await asyncio.sleep(HEARTBEAT_INTERVAL)
            except Exception:
                break

    # ------------------------------------------------------------------
    # MESSAGE HANDLING
    # ------------------------------------------------------------------

    async def _handle_message(self, raw: str) -> None:
        """
        Parse and dispatch incoming messages.
        """
        try:
            data: Dict[str, Any] = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Invalid WS message: %s", raw)
            return

        msg_type = data.get("type")

        if msg_type == "progress":
            value = float(data.get("value", 0.0))
            self._signals.generation_progress.emit(value)
            self._state.update_generation_progress(value)

        elif msg_type == "preview":
            self._signals.generation_preview.emit(data.get("data", {}))

        elif msg_type == "status":
            logger.info("Backend status: %s", data)

        elif msg_type == "error":
            error = data.get("error", "Unknown error")
            self._signals.generation_failed.emit(error)
            self._state.fail_generation(error)

        elif msg_type == "completed":
            self._signals.generation_finished.emit(data)
            self._state.finish_generation()

    # ------------------------------------------------------------------
    # SEND CONTROL MESSAGES
    # ------------------------------------------------------------------

    async def send_cancel(self) -> None:
        """
        Request generation cancellation.
        """
        if self._ws:
            await self._ws.send(json.dumps({"type": "cancel"}))
            self._signals.generation_cancelled.emit()


# =============================================================================
# GLOBAL SINGLETON ACCESSOR
# =============================================================================

_ws_client: Optional[WebSocketClient] = None


def get_ws_client() -> WebSocketClient:
    """
    Global WebSocket client accessor.

    Ensures:
    - one connection
    - centralized lifecycle
    """
    global _ws_client
    if _ws_client is None:
        _ws_client = WebSocketClient()
    return _ws_client
