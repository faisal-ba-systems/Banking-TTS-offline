import re

from pydantic import BaseModel, Field, field_validator

from app.modules.tts.schemas import ProsodySettings


class AnnouncementRequest(BaseModel):
    token_number: str = Field(
        min_length=1,
        max_length=20,
        description="Queue token identifier, e.g. 'B13'",
        examples=["B13"],
    )
    counter_number: str = Field(
        min_length=1,
        max_length=10,
        description="Counter/window number, e.g. '23'",
        examples=["23"],
    )
    language: str = Field(
        default="en",
        description="ISO 639-1 language code",
        examples=["en", "es", "ar", "zh", "ja", "fr"],
    )
    prosody: ProsodySettings = Field(
        default_factory=ProsodySettings,
        description=(
            "Optional prosody settings: speed (0.5–2.0), pitch in semitones (−12 to +12), "
            "volume (0.1–3.0), voice_id for multi-speaker models"
        ),
    )

    @field_validator("token_number", "counter_number")
    @classmethod
    def only_alphanumeric(cls, v: str) -> str:
        if not re.match(r"^[A-Za-z0-9]+$", v):
            raise ValueError("Only letters and digits are allowed.")
        return v.upper()

    @field_validator("language")
    @classmethod
    def lowercase_language(cls, v: str) -> str:
        return v.lower()


class AnnouncementPreviewResponse(BaseModel):
    """Text that would be spoken, without audio synthesis."""
    announcement_text: str
    token_number: str
    counter_number: str
    language: str


class AnnouncementSynthesizeResponse(BaseModel):
    """Metadata returned alongside the audio (as response headers)."""
    announcement_text: str
    language: str
    duration_seconds: float
    model_name: str
