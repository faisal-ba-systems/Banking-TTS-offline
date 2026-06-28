from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response

from app.modules.tts.schemas import TTSSynthesizeRequest, TTSSynthesizeTextResponse, TTSStatusResponse
from app.modules.tts.service import TTSService
from app.modules.language.service import LanguageService

router = APIRouter(prefix="/tts", tags=["TTS"])


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
        result = await tts.synthesize(body.text, body.language, body.voice_id)
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
