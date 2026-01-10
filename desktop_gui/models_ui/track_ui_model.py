from dataclasses import dataclass, field
from typing import List, Dict, Optional
from uuid import uuid4
from enum import Enum


class TrackType(Enum):
    AUDIO = "audio"
    MIDI = "midi"
    AI = "ai"
    STEM = "stem"


class TrackStatus(Enum):
    IDLE = "idle"
    GENERATING = "generating"
    READY = "ready"
    ERROR = "error"
    MUTED = "muted"
    SOLO = "solo"


@dataclass
class PluginUIState:
    plugin_id: str
    name: str
    enabled: bool = True
    parameters: Dict[str, float] = field(default_factory=dict)


@dataclass
class AutomationLaneUI:
    parameter: str
    points: List[Dict[str, float]] = field(default_factory=list)
    visible: bool = True


@dataclass
class TrackUIModel:
    """
    Enterprise-grade UI state model for a track.
    Synchronizes Create, Studio, Chat and backend engines.
    """

    track_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = "New Track"
    track_type: TrackType = TrackType.AI

    status: TrackStatus = TrackStatus.IDLE

    volume: float = 0.8
    pan: float = 0.0

    muted: bool = False
    solo: bool = False
    armed: bool = False

    color: str = "#3A86FF"
    icon: Optional[str] = None

    plugins: List[PluginUIState] = field(default_factory=list)
    automation_lanes: List[AutomationLaneUI] = field(default_factory=list)

    generation_params_id: Optional[str] = None
    last_generation_prompt: Optional[str] = None
    reference_tracks: List[str] = field(default_factory=list)

    waveform_path: Optional[str] = None
    midi_path: Optional[str] = None
    stem_paths: Dict[str, str] = field(default_factory=dict)

    length_seconds: float = 0.0
    bpm: Optional[int] = None
    key: Optional[str] = None

    error_message: Optional[str] = None

    def toggle_mute(self):
        self.muted = not self.muted
        self.status = TrackStatus.MUTED if self.muted else TrackStatus.READY

    def toggle_solo(self):
        self.solo = not self.solo
        self.status = TrackStatus.SOLO if self.solo else TrackStatus.READY

    def add_plugin(self, plugin: PluginUIState):
        self.plugins.append(plugin)

    def remove_plugin(self, plugin_id: str):
        self.plugins = [p for p in self.plugins if p.plugin_id != plugin_id]

    def add_automation_lane(self, lane: AutomationLaneUI):
        self.automation_lanes.append(lane)

    def reset_generation_state(self):
        self.status = TrackStatus.IDLE
        self.last_generation_prompt = None
        self.reference_tracks.clear()

    def mark_generating(self, prompt: str):
        self.status = TrackStatus.GENERATING
        self.last_generation_prompt = prompt

    def mark_ready(self, waveform_path: str, length: float):
        self.status = TrackStatus.READY
        self.waveform_path = waveform_path
        self.length_seconds = length

    def mark_error(self, message: str):
        self.status = TrackStatus.ERROR
        self.error_message = message
