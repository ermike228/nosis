"""
NOSIS Desktop GUI – gRPC Client (Generation Pipeline)
====================================================

Enterprise-grade gRPC client for high-performance AI generation (2025–2026).

Purpose:
- Low-latency, streaming-safe communication with generation backend
- Designed for long-running, heavy ML workloads
- Async-first, UI-safe
- Event-driven integration with GUI

This module contains:
- NO UI code
- NO ML logic
- NO business logic

It is a transport layer between GUI and generation engine.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional, AsyncIterator, Dict, Any

import grpc
import grpc.aio

from desktop_gui.core.signals import get_signals
from desktop_gui.core.app_state import get_app_state

# =============================================================================
# CONFIGURATION
# =============================================================================

DEFAULT_GRPC_ENDPOINT = "localhost:50051"

logger = logging.getLogger("nosis.grpc_client")

# =============================================================================
# GRPC CLIENT
# =============================================================================

class GRPCGenerationClient:
    """
    Async gRPC client for AI music generation.

    Design goals:
    - Streaming-first
    - Non-blocking GUI
    - Clean cancellation
    - Resilient to backend restarts

    This client assumes:
    - Unary → stream OR stream → stream generation
    - Progressive previews
    """

    def __init__(self, endpoint: str = DEFAULT_GRPC_ENDPOINT):
        self._endpoint = endpoint
        self._state = get_app_state()
        self._signals = get_signals()

        self._channel: Optional[grpc.aio.Channel] = None
        self._connected: bool = False

    # ------------------------------------------------------------------
    # CONNECTION MANAGEMENT
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """
        Establish gRPC channel.
        """
        if self._connected:
            return

        self._channel = grpc.aio.insecure_channel(self._endpoint)
        await self._channel.channel_ready()

        self._connected = True
        logger.info("Connected to gRPC backend at %s", self._endpoint)
        self._signals.backend_connected.emit()

    async def close(self) -> None:
        """
        Gracefully close channel.
        """
        if self._channel:
            await self._channel.close()
            self._connected = False
            logger.info("gRPC channel closed")
            self._signals.backend_disconnected.emit()

    # ------------------------------------------------------------------
    # GENERATION PIPELINE
    # ------------------------------------------------------------------

    async def generate(
        self,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        High-level generation entrypoint.

        This method:
        - handles connection lifecycle
        - streams progress & previews
        - returns final result metadata

        The request dict is converted to protobuf upstream
        (bridge responsibility).
        """

        await self.connect()

        self._signals.generation_started.emit()
        self._state.start_generation()

        try:
            result = await self._run_generation_stream(request)
            self._signals.generation_finished.emit(result)
            self._state.finish_generation()
            return result

        except asyncio.CancelledError:
            self._signals.generation_cancelled.emit()
            raise

        except Exception as exc:
            logger.exception("Generation failed")
            self._signals.generation_failed.emit(str(exc))
            self._state.fail_generation(str(exc))
            raise

    # ------------------------------------------------------------------
    # STREAM HANDLING
    # ------------------------------------------------------------------

    async def _run_generation_stream(
        self,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Internal streaming handler.

        NOTE:
        Protobuf stubs are intentionally abstracted here.
        This keeps GUI independent of .proto schema churn.
        """

        # Placeholder for real stub usage:
        # stub = generation_pb2_grpc.GenerationStub(self._channel)
        # stream = stub.Generate(generation_pb2.GenerateRequest(**request))

        # --- Simulated streaming structure (logic, not ML) ---
        async for message in self._fake_stream(request):
            self._handle_stream_message(message)

        # Final metadata (normally last message)
        return {
            "status": "completed",
            "tracks": [],
            "metadata": {},
        }

    async def _fake_stream(self, request: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """
        Stand-in stream iterator to demonstrate flow.

        Replace with real gRPC stream.
        """
        for i in range(1, 11):
            await asyncio.sleep(0.3)
            yield {
                "type": "progress",
                "value": i / 10.0,
            }

        yield {
            "type": "preview",
            "data": {"audio_chunk": b"..."},
        }

    # ------------------------------------------------------------------
    # MESSAGE DISPATCH
    # ------------------------------------------------------------------

    def _handle_stream_message(self, message: Dict[str, Any]) -> None:
        """
        Dispatch stream messages to UI via signals.
        """
        msg_type = message.get("type")

        if msg_type == "progress":
            value = float(message.get("value", 0.0))
            self._signals.generation_progress.emit(value)
            self._state.update_generation_progress(value)

        elif msg_type == "preview":
            self._signals.generation_preview.emit(message.get("data", {}))

        elif msg_type == "error":
            raise RuntimeError(message.get("error"))

# =============================================================================
# GLOBAL SINGLETON ACCESSOR
# =============================================================================

_grpc_client: Optional[GRPCGenerationClient] = None


def get_grpc_client() -> GRPCGenerationClient:
    """
    Global accessor for gRPC generation client.

    Ensures:
    - single channel per app
    - predictable lifecycle
    """
    global _grpc_client
    if _grpc_client is None:
        _grpc_client = GRPCGenerationClient()
    return _grpc_client
