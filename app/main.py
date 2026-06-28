import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import Settings, get_settings
from app.modules.announcement.service import AnnouncementService
from app.modules.health.service import HealthService
from app.modules.language.service import LanguageService
from app.modules.tts.service import TTSService
from app.modules.voice.service import VoiceService

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = get_settings()
    logger.info("Starting %s…", settings.APP_NAME)

    # Wire up services (dependency graph: language → tts → announcement)
    language_service = LanguageService(settings)
    voice_service = VoiceService()
    tts_service = TTSService(settings, language_service)
    announcement_service = AnnouncementService(tts_service, language_service)
    health_service = HealthService(settings, tts_service, language_service)

    # Attach to app state so routes can access them via request.app.state
    app.state.settings = settings
    app.state.language_service = language_service
    app.state.voice_service = voice_service
    app.state.tts_service = tts_service
    app.state.announcement_service = announcement_service
    app.state.health_service = health_service

    logger.info("%s started successfully", settings.APP_NAME)
    yield
    logger.info("%s shutting down", settings.APP_NAME)


# ── Application factory ───────────────────────────────────────────────────────
def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "Offline Text-to-Speech Announcement System for banking queue management. "
            "Converts token and counter numbers into spoken audio using Coqui TTS."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Global exception handler ───────────────────────────────────────────────
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred. See server logs for details."},
        )

    # ── Routers ───────────────────────────────────────────────────────────────
    from app.modules.health.routes import router as health_router
    from app.modules.language.routes import router as language_router
    from app.modules.voice.routes import router as voice_router
    from app.modules.tts.routes import router as tts_router
    from app.modules.announcement.routes import router as announcement_router

    prefix = settings.API_V1_PREFIX
    app.include_router(health_router, prefix=prefix)
    app.include_router(language_router, prefix=prefix)
    app.include_router(voice_router, prefix=prefix)
    app.include_router(tts_router, prefix=prefix)
    app.include_router(announcement_router, prefix=prefix)

    # ── Static UI ─────────────────────────────────────────────────────────────
    static_dir = os.path.join(os.path.dirname(__file__), "static")

    @app.get("/", include_in_schema=False)
    def serve_ui() -> FileResponse:
        return FileResponse(os.path.join(static_dir, "index.html"))

    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    return app


app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
