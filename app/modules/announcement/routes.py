from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response

from app.modules.announcement.schemas import (
    AnnouncementPreviewResponse,
    AnnouncementRequest,
)
from app.modules.announcement.service import AnnouncementService
from app.modules.language.service import LanguageService

router = APIRouter(prefix="/announcements", tags=["Announcements"])


def _get_announcement_service(request: Request) -> AnnouncementService:
    return request.app.state.announcement_service


def _get_language_service(request: Request) -> LanguageService:
    return request.app.state.language_service


@router.post(
    "",
    response_class=Response,
    responses={
        200: {
            "content": {"audio/wav": {}},
            "description": "WAV audio of the announcement",
            "headers": {
                "X-Announcement-Text": {"description": "The spoken text"},
                "X-Audio-Duration": {"description": "Audio duration in seconds"},
                "X-Language": {"description": "Language code used"},
                "X-Model": {"description": "TTS model used"},
            },
        }
    },
    summary="Synthesize a queue announcement",
    description=(
        "Accepts a token number and counter number, expands digits character-by-character "
        "(e.g. '23' → 'two three'), renders the language template, and returns WAV audio."
    ),
)
async def synthesize_announcement(
    body: AnnouncementRequest,
    lang_svc: LanguageService = Depends(_get_language_service),
    svc: AnnouncementService = Depends(_get_announcement_service),
) -> Response:
    if not lang_svc.is_supported(body.language):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language '{body.language}' is not supported. Supported: {lang_svc.supported_codes()}",
        )
    try:
        result = await svc.synthesize(
            token_number=body.token_number,
            counter_number=body.counter_number,
            language=body.language,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return Response(
        content=result.audio.wav_bytes,
        media_type="audio/wav",
        headers={
            "X-Announcement-Text": result.announcement_text,
            "X-Audio-Duration": f"{result.audio.duration_seconds:.3f}",
            "X-Language": body.language,
            "X-Model": result.audio.model_name,
        },
    )


@router.post(
    "/preview",
    response_model=AnnouncementPreviewResponse,
    summary="Preview announcement text without synthesizing audio",
)
def preview_announcement(
    body: AnnouncementRequest,
    lang_svc: LanguageService = Depends(_get_language_service),
    svc: AnnouncementService = Depends(_get_announcement_service),
) -> AnnouncementPreviewResponse:
    if not lang_svc.is_supported(body.language):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language '{body.language}' is not supported. Supported: {lang_svc.supported_codes()}",
        )
    text = svc.build_preview_text(
        token_number=body.token_number,
        counter_number=body.counter_number,
        language=body.language,
    )
    return AnnouncementPreviewResponse(
        announcement_text=text,
        token_number=body.token_number,
        counter_number=body.counter_number,
        language=body.language,
    )
