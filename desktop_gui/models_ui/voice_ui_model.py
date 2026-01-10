
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import uuid
import time


class VoiceGender(Enum):
    MALE = "male"
    FEMALE = "female"
    ANDROGYNOUS = "androgynous"
    CHILD = "child"
    UNKNOWN = "unknown"


class VoiceRegister(Enum):
    BASS = "bass"
    BARITONE = "baritone"
    TENOR = "tenor"
    ALTO = "alto"
    MEZZO_SOPRANO = "mezzo_soprano"
    SOPRANO = "soprano"
    COUNTERTENOR = "countertenor"
    UNSPECIFIED = "unspecified"


class VoiceEmotion(Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    DARK = "dark"
    HOPEFUL = "hopeful"
    AGGRESSIVE = "aggressive"
    CALM = "calm"
    EPIC = "epic"
    INTIMATE = "intimate"


@dataclass
class VoiceTechnicalProfile:
    pitch_range_min: float = 80.0
    pitch_range_max: float = 1200.0
    formant_shift: float = 0.0
    vibrato_depth: float = 0.0
    vibrato_rate: float = 0.0
    breathiness: float = 0.0
    roughness: float = 0.0
    nasality: float = 0.0
    clarity: float = 1.0


@dataclass
class VoiceStyleProfile:
    emotion: VoiceEmotion = VoiceEmotion.NEUTRAL
    intensity: float = 0.5
    articulation: float = 0.5
    expressiveness: float = 0.5
    legato: float = 0.5
    rhythmic_precision: float = 0.5


@dataclass
class VoiceIdentity:
    voice_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Unnamed Voice"
    gender: VoiceGender = VoiceGender.UNKNOWN
    register: VoiceRegister = VoiceRegister.UNSPECIFIED
    language: str = "en"
    description: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class VoiceUIModel:
    identity: VoiceIdentity = field(default_factory=VoiceIdentity)
    technical: VoiceTechnicalProfile = field(default_factory=VoiceTechnicalProfile)
    style: VoiceStyleProfile = field(default_factory=VoiceStyleProfile)

    enabled: bool = True
    locked_identity: bool = False
    locked_style: bool = False
    locked_technical: bool = False

    last_modified: float = field(default_factory=time.time)
    version: int = 1

    _listeners: Dict[str, List[Callable[[Any], None]]] = field(default_factory=dict, init=False)

    def subscribe(self, event: str, callback: Callable[[Any], None]) -> None:
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def _emit(self, event: str, payload: Any = None) -> None:
        for cb in self._listeners.get(event, []):
            cb(payload)

    def _touch(self) -> None:
        self.last_modified = time.time()
        self.version += 1
        self._emit("updated", self)

    def set_voice_identity(self, **kwargs) -> None:
        if self.locked_identity:
            return
        for key, value in kwargs.items():
            if hasattr(self.identity, key):
                setattr(self.identity, key, value)
        self._emit("identity_changed", self.identity)
        self._touch()

    def set_style(self, **kwargs) -> None:
        if self.locked_style:
            return
        for key, value in kwargs.items():
            if hasattr(self.style, key):
                setattr(self.style, key, value)
        self._emit("style_changed", self.style)
        self._touch()

    def set_technical(self, **kwargs) -> None:
        if self.locked_technical:
            return
        for key, value in kwargs.items():
            if hasattr(self.technical, key):
                setattr(self.technical, key, value)
        self._emit("technical_changed", self.technical)
        self._touch()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": vars(self.identity),
            "technical": vars(self.technical),
            "style": {
                "emotion": self.style.emotion.value,
                "intensity": self.style.intensity,
                "articulation": self.style.articulation,
                "expressiveness": self.style.expressiveness,
                "legato": self.style.legato,
                "rhythmic_precision": self.style.rhythmic_precision,
            },
            "enabled": self.enabled,
            "locks": {
                "identity": self.locked_identity,
                "style": self.locked_style,
                "technical": self.locked_technical,
            },
            "version": self.version,
            "last_modified": self.last_modified,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VoiceUIModel":
        model = cls()
        id_data = data.get("identity", {})
        model.identity = VoiceIdentity(
            voice_id=id_data.get("voice_id", model.identity.voice_id),
            name=id_data.get("name", ""),
            gender=VoiceGender(id_data.get("gender", VoiceGender.UNKNOWN.value)),
            register=VoiceRegister(id_data.get("register", VoiceRegister.UNSPECIFIED.value)),
            language=id_data.get("language", "en"),
            description=id_data.get("description", ""),
            tags=id_data.get("tags", []),
        )
        return model
