
"""
nosis.desktop_gui.models_ui.generation_params

Enterprise-grade unified generation parameter model.
Acts as the single source of truth between:
- GUI (Create / Studio / Chat)
- Backend (REST / gRPC / WS)
- AI models (music, voice, lyrics, image)
- Project persistence & versioning

2026-ready, extensible, non-breaking design.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Optional, Any
import json
import uuid
import time


# =========================
# ENUMS
# =========================

class GenerationMode(str, Enum):
    SONG = "song"
    INSTRUMENTAL = "instrumental"
    STEM = "stem"
    DAW_TRACK = "daw_track"
    DAW_REGION = "daw_region"
    REGENERATION = "regeneration"


class OutputFormat(str, Enum):
    WAV = "wav"
    FLAC = "flac"
    MP3 = "mp3"


class StereoMode(str, Enum):
    MONO = "mono"
    STEREO = "stereo"
    WIDE = "wide"
    BINAURAL = "binaural"


# =========================
# CORE BLOCKS
# =========================

@dataclass
class PromptBlock:
    lyrics: str = ""
    style: str = ""
    negative: str = ""
    max_characters: int = 10000

    def validate(self) -> List[str]:
        errors = []
        if len(self.lyrics) > self.max_characters:
            errors.append("Lyrics prompt exceeds maximum length")
        if len(self.style) > self.max_characters:
            errors.append("Style prompt exceeds maximum length")
        return errors


@dataclass
class ReferenceAudio:
    path: str
    weight_structure: float = 0.5
    weight_timbre: float = 0.5
    weight_style: float = 0.5


@dataclass
class ReferenceBlock:
    audios: List[ReferenceAudio] = field(default_factory=list)
    max_references: int = 10

    def validate(self) -> List[str]:
        errors = []
        if len(self.audios) > self.max_references:
            errors.append("Too many reference audios")
        return errors


@dataclass
class GenreBlock:
    primary: str = ""
    secondary: List[str] = field(default_factory=list)
    interpolation_depth: float = 0.5
    novelty_bias: float = 0.5

    def validate(self) -> List[str]:
        return []


@dataclass
class VoiceBlock:
    enabled: bool = True
    language: str = "en"
    gender: Optional[str] = None
    voice_type: Optional[str] = None
    emotion: Optional[str] = None
    choir_mode: bool = False
    realism_noise: float = 0.15


@dataclass
class MusicTheoryBlock:
    bpm: Optional[int] = None
    key: Optional[str] = None
    time_signature: Optional[str] = None
    structure: Optional[str] = None


@dataclass
class AdvancedControls:
    randomness: float = 0.5
    prompt_accuracy: float = 0.8
    reference_similarity: float = 0.6
    semantic_lock: bool = False
    style_lock: bool = False
    quality_gate: bool = True
    multi_pass: int = 1


@dataclass
class OutputBlock:
    format: OutputFormat = OutputFormat.WAV
    stereo: StereoMode = StereoMode.STEREO
    sample_rate: int = 48000
    bit_depth: int = 24
    mastering: bool = True


# =========================
# ROOT PARAM OBJECT
# =========================

@dataclass
class GenerationParams:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    version: int = 1

    mode: GenerationMode = GenerationMode.SONG

    prompt: PromptBlock = field(default_factory=PromptBlock)
    references: ReferenceBlock = field(default_factory=ReferenceBlock)
    genre: GenreBlock = field(default_factory=GenreBlock)
    voice: VoiceBlock = field(default_factory=VoiceBlock)
    theory: MusicTheoryBlock = field(default_factory=MusicTheoryBlock)
    advanced: AdvancedControls = field(default_factory=AdvancedControls)
    output: OutputBlock = field(default_factory=OutputBlock)

    # Contextual metadata (Studio / Chat / Project)
    context: Dict[str, Any] = field(default_factory=dict)

    # ---------------------
    # VALIDATION
    # ---------------------

    def validate(self) -> List[str]:
        errors: List[str] = []
        errors.extend(self.prompt.validate())
        errors.extend(self.references.validate())
        errors.extend(self.genre.validate())
        return errors

    # ---------------------
    # SERIALIZATION
    # ---------------------

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, pretty: bool = False) -> str:
        if pretty:
            return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @staticmethod
    def from_json(data: str) -> "GenerationParams":
        raw = json.loads(data)
        return GenerationParams._from_dict(raw)

    @staticmethod
    def _from_dict(data: Dict[str, Any]) -> "GenerationParams":
        return GenerationParams(
            id=data.get("id"),
            created_at=data.get("created_at", time.time()),
            version=data.get("version", 1),
            mode=GenerationMode(data.get("mode", GenerationMode.SONG)),
            prompt=PromptBlock(**data.get("prompt", {})),
            references=ReferenceBlock(
                audios=[ReferenceAudio(**a) for a in data.get("references", {}).get("audios", [])]
            ),
            genre=GenreBlock(**data.get("genre", {})),
            voice=VoiceBlock(**data.get("voice", {})),
            theory=MusicTheoryBlock(**data.get("theory", {})),
            advanced=AdvancedControls(**data.get("advanced", {})),
            output=OutputBlock(**data.get("output", {})),
            context=data.get("context", {}),
        )
