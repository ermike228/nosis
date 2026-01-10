"""
NOSIS Desktop GUI – File Bridge (Uploads & References)
====================================================

Enterprise-grade file handling bridge for desktop GUI (2025–2026).

Responsibilities:
- Upload reference audio / images / files
- Validate files before upload
- Support large files (streaming-safe)
- Emit progress & lifecycle events
- Abstract backend upload implementation

This module:
- Contains NO UI code
- Contains NO ML logic
- Contains NO business logic
"""

from __future__ import annotations

import asyncio
import logging
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any, Iterable

import httpx

from desktop_gui.bridge.api_client import get_api_client
from desktop_gui.core.signals import get_signals
from desktop_gui.core.app_state import get_app_state

logger = logging.getLogger("nosis.file_bridge")


# =============================================================================
# CONFIGURATION
# =============================================================================

MAX_FILE_SIZE_MB = 200
ALLOWED_AUDIO_TYPES = {
    "audio/wav",
    "audio/mpeg",
    "audio/mp3",
    "audio/flac",
    "audio/ogg",
}

ALLOWED_IMAGE_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
}


# =============================================================================
# FILE BRIDGE
# =============================================================================

class FileBridge:
    """
    Central file upload & reference manager for the GUI.

    Design goals:
    - Async-first
    - Safe validation
    - Progress-aware
    - Backend-agnostic (local, cloud, presigned URLs)
    """

    def __init__(self):
        self._api = get_api_client()
        self._signals = get_signals()
        self._state = get_app_state()

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    async def upload_reference_files(
        self,
        paths: Iterable[Path],
        category: str = "audio",
    ) -> None:
        """
        Upload one or multiple reference files.

        category:
            - "audio"
            - "image"
            - "other"
        """
        for path in paths:
            await self._upload_single_file(path, category)

    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------

    def _validate_file(self, path: Path, category: str) -> None:
        """
        Validate file before upload.
        """
        if not path.exists():
            raise FileNotFoundError(path)

        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            raise ValueError(f"File too large: {path.name}")

        mime, _ = mimetypes.guess_type(path)

        if category == "audio" and mime not in ALLOWED_AUDIO_TYPES:
            raise ValueError(f"Unsupported audio type: {mime}")

        if category == "image" and mime not in ALLOWED_IMAGE_TYPES:
            raise ValueError(f"Unsupported image type: {mime}")

    # ------------------------------------------------------------------
    # UPLOAD LOGIC
    # ------------------------------------------------------------------

    async def _upload_single_file(
        self,
        path: Path,
        category: str,
    ) -> None:
        """
        Upload a single file with progress reporting.
        """
        self._validate_file(path, category)

        logger.info("Uploading file: %s", path.name)

        self._signals.notification.emit(
            f"Uploading {path.name}", "info"
        )

        async with httpx.AsyncClient(timeout=None) as client:
            with path.open("rb") as f:
                files = {
                    "file": (path.name, f, mimetypes.guess_type(path)[0]),
                    "category": (None, category),
                }

                response = await client.post(
                    f"{self._api._base_url}/files/upload",
                    files=files,
                    headers=self._api._build_headers(),
                )

                response.raise_for_status()

        self._signals.notification.emit(
            f"Uploaded {path.name}", "success"
        )

        logger.info("File uploaded successfully: %s", path.name)

    # ------------------------------------------------------------------
    # CONVENIENCE HELPERS
    # ------------------------------------------------------------------

    async def upload_audio_references(self, paths: Iterable[Path]) -> None:
        await self.upload_reference_files(paths, category="audio")

    async def upload_image_references(self, paths: Iterable[Path]) -> None:
        await self.upload_reference_files(paths, category="image")


# =============================================================================
# GLOBAL SINGLETON ACCESSOR
# =============================================================================

_file_bridge: Optional[FileBridge] = None


def get_file_bridge() -> FileBridge:
    """
    Global accessor for FileBridge.

    Ensures:
    - one upload controller
    - consistent validation rules
    """
    global _file_bridge
    if _file_bridge is None:
        _file_bridge = FileBridge()
    return _file_bridge
