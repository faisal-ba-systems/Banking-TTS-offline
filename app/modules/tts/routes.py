from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response

from app.modules.tts.schemas import (
    ProsodySettings,
    TTSSynthesizeRequest,
    TTSSynthesizeTextResponse,
    TTSStatusResponse,
    VoicePreviewRequest,
)
from app.modules.tts.service import TTSService
from app.modules.language.service import LanguageService

router = APIRouter(prefix="/tts", tags=["TTS"])

# Short sample sentence per language used by the voice preview endpoint.
_PREVIEW_TEXTS: dict[str, str] = {
    "en": "Welcome. Please proceed to your assigned counter.",
    "es": "Bienvenido. Por favor, diríjase a su ventanilla asignada.",
    "ar": "مرحباً. يرجى التوجه إلى النافذة المخصصة لك.",
    "zh": "欢迎。请前往您指定的柜台。",
    "ja": "ようこそ。担当カウンターにお進みください。",
    "fr": "Bienvenue. Veuillez vous diriger vers votre guichet assigné.",
}


def _get_tts_service(request: Request) -> TTSService:
    return request.app.state.tts_service


def _get_language_service(request: Request) -> LanguageService:
    return request.app.state.language_service


@router.post(
    "/synthesize",
    response_class=Response,
    responses={200: {"content": {"audio/wav": {}}, "description": "WAV audio stream"}},
    summary="Synthesize arbitrary text to speech",
)
async def synthesize(
    body: TTSSynthesizeRequest,
    tts: TTSService = Depends(_get_tts_service),
    lang_svc: LanguageService = Depends(_get_language_service),
) -> Response:
    if not lang_svc.is_supported(body.language):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language '{body.language}' is not supported. Supported: {lang_svc.supported_codes()}",
        )
    try:
        result = await tts.synthesize(body.text, body.language, body.prosody)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return Response(
        content=result.wav_bytes,
        media_type="audio/wav",
        headers={"X-Audio-Duration": f"{result.duration_seconds:.3f}"},
    )


@router.post(
    "/preview-voice",
    response_class=Response,
    responses={200: {"content": {"audio/wav": {}}, "description": "Short WAV sample for the requested voice"}},
    summary="Preview a voice with a short sample sentence",
    description=(
        "Synthesizes a fixed sample sentence in the given language using the specified voice. "
        "Use this to audition voices before selecting one for announcements."
    ),
)
async def preview_voice(
    body: VoicePreviewRequest,
    tts: TTSService = Depends(_get_tts_service),
    lang_svc: LanguageService = Depends(_get_language_service),
) -> Response:
    if not lang_svc.is_supported(body.language):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language '{body.language}' is not supported.",
        )
    text = _PREVIEW_TEXTS.get(body.language, _PREVIEW_TEXTS["en"])
    prosody = ProsodySettings(voice_id=body.voice_id)
    try:
        result = await tts.synthesize(text, body.language, prosody)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return Response(
        content=result.wav_bytes,
        media_type="audio/wav",
        headers={"X-Audio-Duration": f"{result.duration_seconds:.3f}"},
    )


@router.get("/status", response_model=TTSStatusResponse, summary="TTS engine status")
def get_status(tts: TTSService = Depends(_get_tts_service)) -> TTSStatusResponse:
    return TTSStatusResponse(
        backend=tts.get_backend_name(),
        loaded_languages=tts.get_loaded_languages(),
        use_gpu=tts._settings.TTS_USE_GPU,
    )
