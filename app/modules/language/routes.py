from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.modules.language.schemas import LanguageDetailResponse, LanguageListResponse
from app.modules.language.service import LanguageService

router = APIRouter(prefix="/languages", tags=["Languages"])


def _get_language_service(request: Request) -> LanguageService:
    return request.app.state.language_service


@router.get("", response_model=LanguageListResponse, summary="List supported languages")
def list_languages(service: LanguageService = Depends(_get_language_service)) -> LanguageListResponse:
    languages = service.list_all()
    return LanguageListResponse(languages=languages, total=len(languages))


@router.get(
    "/{code}",
    response_model=LanguageDetailResponse,
    summary="Get language details by ISO 639-1 code",
)
def get_language(code: str, service: LanguageService = Depends(_get_language_service)) -> LanguageDetailResponse:
    if not service.is_supported(code):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Language '{code}' is not supported. Supported codes: {service.supported_codes()}",
        )
    return LanguageDetailResponse(**service.get(code).model_dump())
