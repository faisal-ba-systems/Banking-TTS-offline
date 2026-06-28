from fastapi import APIRouter, Depends, Query, Request
from app.modules.voice.schemas import VoiceListResponse
from app.modules.voice.service import VoiceService
from app.modules.tts.service import TTSService

router = APIRouter(prefix="/voices", tags=["Voices"])


def _get_voice_service(request: Request) -> VoiceService:
    return request.app.state.voice_service


def _get_tts_service(request: Request) -> TTSService:
    return request.app.state.tts_service


@router.get(
    "",
    response_model=VoiceListResponse,
    summary="List available TTS voices",
    description=(
        "Returns voices for the active backend.\n\n"
        "- **Single-speaker backend**: one voice per language (voice_id has no effect on audio).\n"
        "- **XTTS v2 backend**: 54 multilingual speakers; use `gender` to filter by `male`/`female`."
    ),
)
def list_voices(
    language: str | None = Query(default=None, description="Filter by ISO 639-1 language code (single-speaker backend only)"),
    gender: str | None = Query(default=None, description="Filter by gender: 'male' or 'female' (XTTS backend only)"),
    service: VoiceService = Depends(_get_voice_service),
    tts: TTSService = Depends(_get_tts_service),
) -> VoiceListResponse:
    if tts.get_backend_name() == "CoquiXTTSBackend":
        voices = service.list_xtts_voices(gender=gender)
    else:
        voices = service.list_voices(language_code=language)
    return VoiceListResponse(voices=voices, total=len(voices), language_code=language)
