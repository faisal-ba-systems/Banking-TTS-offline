from pydantic import BaseModel, Field


class ProsodySettings(BaseModel):
    """Fine-grained control over synthesized speech characteristics."""

    speed: float = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="Speech rate multiplier (0.5 = half speed, 1.0 = normal, 2.0 = double speed)",
    )
    pitch: float = Field(
        default=0.0,
        ge=-12.0,
        le=12.0,
        description="Pitch shift in semitones (negative = lower / more masculine, positive = higher / more feminine)",
    )
    volume: float = Field(
        default=1.0,
        ge=0.1,
        le=3.0,
        description="Volume multiplier (1.0 = original, 2.0 = twice as loud)",
    )
    voice_id: str | None = Field(
        default=None,
        description="Speaker voice ID — used by multi-speaker or XTTS models",
    )


class TTSSynthesizeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000, description="Plain text to synthesize")
    language: str = Field(default="en", description="ISO 639-1 language code")
    prosody: ProsodySettings = Field(
        default_factory=ProsodySettings,
        description="Optional prosody/voice control (speed, pitch, volume, voice_id)",
    )


class VoicePreviewRequest(BaseModel):
    """Request body for POST /tts/preview-voice."""
    voice_id: str = Field(description="XTTS v2 built-in speaker name to audition")
    language: str = Field(default="en", description="ISO 639-1 language code for the sample sentence")


class TTSSynthesizeTextResponse(BaseModel):
    """Returned by the /tts/preview endpoint (text only, no audio)."""
    text: str
    language: str
    model_name: str
    character_count: int


class TTSStatusResponse(BaseModel):
    backend: str
    loaded_languages: list[str]
    use_gpu: bool
