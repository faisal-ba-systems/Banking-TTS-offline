from fastapi import APIRouter, Depends, Request
from app.modules.health.schemas import HealthResponse
from app.modules.health.service import HealthService

router = APIRouter(prefix="/health", tags=["Health"])


def _get_health_service(request: Request) -> HealthService:
    return request.app.state.health_service


@router.get("", response_model=HealthResponse, summary="Application health check")
def health_check(service: HealthService = Depends(_get_health_service)) -> HealthResponse:
    return service.check()
