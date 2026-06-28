from pydantic import BaseModel, Field


class VoiceInfo(BaseModel):
    voice_id: str = Field(description="Unique identifier for this voice")
    name: str = Field(description="Human-readable voice name")
    language_code: str = Field(description="ISO 639-1 language code")
    gender: str | None = Field(default=None, description="Speaker gender hint, if known")
    is_default: bool = Field(default=False, description="Whether this is the default voice for the language")
    description: str | None = Field(default=None)


class VoiceListResponse(BaseModel):
    voices: list[VoiceInfo]
    total: int
    language_code: str | None = None
