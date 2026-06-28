from fastapi import APIRouter, Depends, Query, Request
from app.modules.voice.schemas import VoiceListResponse
from app.modules.voice.service import VoiceService

router = APIRouter(prefix="/voices", tags=["Voices"])


def _get_voice_service(request: Request) -> VoiceService:
    return request.app.state.voice_service


@router.get("", response_model=VoiceListResponse, summary="List available TTS voices")
def list_voices(
    language: str | None = Query(default=None, description="Filter by ISO 639-1 language code"),
    service: VoiceService = Depends(_get_voice_service),
) -> VoiceListResponse:
    voices = service.list_voices(language_code=language)
    return VoiceListResponse(voices=voices, total=len(voices), language_code=language)
