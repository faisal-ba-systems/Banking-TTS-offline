from pydantic import BaseModel, Field


class TTSSynthesizeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000, description="Plain text to synthesize")
    language: str = Field(default="en", description="ISO 639-1 language code")
    voice_id: str | None = Field(default=None, description="Optional voice identifier")


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
