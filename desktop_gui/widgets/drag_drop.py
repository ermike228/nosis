
"""
NOSIS Drag & Drop Framework
Enterprise-level drag & drop infrastructure for audio, image, MIDI, and semantic assets.

Level: Lead Enterprise 2026
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
import os


class DragPayload:
    """
    Unified drag payload abstraction.
    Used across Create / Studio / Chat / Library.
    """

    def __init__(self, paths=None, payload_type=None, metadata=None):
        self.paths = paths or []
        self.payload_type = payload_type  # audio, image, midi, text, semantic
        self.metadata = metadata or {}

    def is_audio(self):
        return self.payload_type == "audio"

    def is_image(self):
        return self.payload_type == "image"

    def is_midi(self):
        return self.payload_type == "midi"

    def is_text(self):
        return self.payload_type == "text"

    def is_semantic(self):
        return self.payload_type == "semantic"


class DragDropWidget(QWidget):
    """
    Base widget with enterprise-grade drag & drop support.
    """

    dragEntered = pyqtSignal(DragPayload)
    dropped = pyqtSignal(DragPayload)
    dragLeft = pyqtSignal()

    SUPPORTED_AUDIO = {".wav", ".mp3", ".flac", ".ogg", ".aiff"}
    SUPPORTED_IMAGE = {".png", ".jpg", ".jpeg", ".webp"}
    SUPPORTED_MIDI = {".mid", ".midi"}
    SUPPORTED_TEXT = {".txt", ".md"}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        payload = self._parse_event(event)
        if payload:
            event.acceptProposedAction()
            self.dragEntered.emit(payload)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.dragLeft.emit()
        event.accept()

    def dropEvent(self, event: QDropEvent):
        payload = self._parse_event(event)
        if payload:
            event.acceptProposedAction()
            self.dropped.emit(payload)
        else:
            event.ignore()

    def _parse_event(self, event):
        mime = event.mimeData()

        if mime.hasUrls():
            paths = [url.toLocalFile() for url in mime.urls()]
            extensions = {os.path.splitext(p)[1].lower() for p in paths}

            if extensions & self.SUPPORTED_AUDIO:
                return DragPayload(paths, "audio")

            if extensions & self.SUPPORTED_IMAGE:
                return DragPayload(paths, "image")

            if extensions & self.SUPPORTED_MIDI:
                return DragPayload(paths, "midi")

            if extensions & self.SUPPORTED_TEXT:
                return DragPayload(paths, "text")

        if mime.hasText():
            return DragPayload(
                paths=[],
                payload_type="semantic",
                metadata={"text": mime.text()}
            )

        return None
