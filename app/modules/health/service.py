import logging
import os

from app.config import Settings
from app.modules.health.schemas import ComponentHealth, HealthResponse, HealthStatus
from app.modules.language.service import LanguageService
from app.modules.tts.service import TTSService

logger = logging.getLogger(__name__)


class HealthService:
    def __init__(self, settings: Settings, tts_service: TTSService, language_service: LanguageService) -> None:
        self._settings = settings
        self._tts = tts_service
        self._language_service = language_service

    def check(self) -> HealthResponse:
        components: list[ComponentHealth] = [
            self._check_tts_backend(),
            self._check_languages(),
            self._check_model_cache_dir(),
        ]
        overall = (
            HealthStatus.OK
            if all(c.status == HealthStatus.OK for c in components)
            else HealthStatus.DEGRADED
        )
        return HealthResponse(
            status=overall,
            app_name=self._settings.APP_NAME,
            components=components,
        )

    def _check_tts_backend(self) -> ComponentHealth:
        try:
            backend = self._tts.get_backend_name()
            loaded = self._tts.get_loaded_languages()
            detail = f"backend={backend}, loaded_languages={loaded or 'none (lazy)'}"
            return ComponentHealth(name="tts_backend", status=HealthStatus.OK, detail=detail)
        except Exception as exc:
            logger.warning("TTS backend health check failed: %s", exc)
            return ComponentHealth(name="tts_backend", status=HealthStatus.DEGRADED, detail=str(exc))

    def _check_languages(self) -> ComponentHealth:
        codes = self._language_service.supported_codes()
        return ComponentHealth(
            name="languages",
            status=HealthStatus.OK,
            detail=f"{len(codes)} supported: {', '.join(codes)}",
        )

    def _check_model_cache_dir(self) -> ComponentHealth:
        cache_dir = self._settings.TTS_MODELS_CACHE_DIR
        try:
            os.makedirs(cache_dir, exist_ok=True)
            test_path = os.path.join(cache_dir, ".write_test")
            with open(test_path, "w") as f:
                f.write("ok")
            os.remove(test_path)
            return ComponentHealth(name="model_cache_dir", status=HealthStatus.OK, detail=cache_dir)
        except OSError as exc:
            return ComponentHealth(name="model_cache_dir", status=HealthStatus.DEGRADED, detail=str(exc))
