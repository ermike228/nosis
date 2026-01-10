
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from uuid import uuid4
from datetime import datetime

try:
    from PyQt6.QtCore import QObject, pyqtSignal
except ImportError:
    QObject = object
    def pyqtSignal(*args, **kwargs):
        return None


class ProjectSignals(QObject):
    """
    Centralized signal bus for Project UI Model.
    """
    projectChanged = pyqtSignal()
    trackAdded = pyqtSignal(str)
    trackRemoved = pyqtSignal(str)
    projectSaved = pyqtSignal(str)
    projectLoaded = pyqtSignal(str)


@dataclass
class ProjectMetadata:
    """
    Metadata describing the project.
    """
    title: str
    author: str
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    genre: Optional[str] = None
    bpm: Optional[int] = None
    time_signature: str = "4/4"


@dataclass
class ProjectSettings:
    """
    Global project-level settings.
    """
    sample_rate: int = 48000
    bit_depth: int = 24
    stereo: bool = True
    loudness_target_lufs: float = -14.0
    enable_ai_assist: bool = True
    auto_save_interval_sec: int = 120


class ProjectUIModel(QObject):
    """
    Enterprise-grade Project UI Model.

    Responsibilities:
    - Single source of truth for project state in GUI
    - Synchronization point between Create / Studio / Chat
    - Emits signals for reactive UI updates
    - Safe for enterprise-scale feature growth
    """

    def __init__(self, metadata: ProjectMetadata, settings: Optional[ProjectSettings] = None):
        super().__init__()
        self.id: str = str(uuid4())
        self.metadata: ProjectMetadata = metadata
        self.settings: ProjectSettings = settings or ProjectSettings()
        self.tracks: Dict[str, Any] = {}
        self.signals = ProjectSignals()
        self._dirty: bool = False

    def mark_dirty(self) -> None:
        self._dirty = True
        self.metadata.updated_at = datetime.utcnow()
        if self.signals.projectChanged:
            self.signals.projectChanged.emit()

    def is_dirty(self) -> bool:
        return self._dirty

    def save(self, path: str) -> None:
        self._dirty = False
        if self.signals.projectSaved:
            self.signals.projectSaved.emit(path)

    def load(self, path: str) -> None:
        self._dirty = False
        if self.signals.projectLoaded:
            self.signals.projectLoaded.emit(path)

    def add_track(self, track_model: Any) -> str:
        track_id = getattr(track_model, "track_id", str(uuid4()))
        self.tracks[track_id] = track_model
        self.mark_dirty()
        if self.signals.trackAdded:
            self.signals.trackAdded.emit(track_id)
        return track_id

    def remove_track(self, track_id: str) -> None:
        if track_id in self.tracks:
            del self.tracks[track_id]
            self.mark_dirty()
            if self.signals.trackRemoved:
                self.signals.trackRemoved.emit(track_id)

    def get_track(self, track_id: str) -> Optional[Any]:
        return self.tracks.get(track_id)

    def list_tracks(self) -> List[Any]:
        return list(self.tracks.values())

    def apply_generation_params(self, params: Dict[str, Any]) -> None:
        if "bpm" in params:
            self.metadata.bpm = params["bpm"]
        if "genre" in params:
            self.metadata.genre = params["genre"]
        self.mark_dirty()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "metadata": {
                "title": self.metadata.title,
                "author": self.metadata.author,
                "description": self.metadata.description,
                "tags": self.metadata.tags,
                "genre": self.metadata.genre,
                "bpm": self.metadata.bpm,
                "time_signature": self.metadata.time_signature,
            },
            "settings": {
                "sample_rate": self.settings.sample_rate,
                "bit_depth": self.settings.bit_depth,
                "stereo": self.settings.stereo,
                "loudness_target_lufs": self.settings.loudness_target_lufs,
            },
            "tracks_count": len(self.tracks),
            "dirty": self._dirty,
        }
