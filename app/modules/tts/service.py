import asyncio
import logging

from app.config import Settings
from app.modules.language.service import LanguageService
from app.modules.tts.backends.base import ITTSBackend, RawAudio
from app.modules.tts.backends.coqui_single import CoquiSingleSpeakerBackend
from app.modules.tts.backends.coqui_xtts import CoquiXTTSBackend

logger = logging.getLogger(__name__)


class TTSService:
    """
    Orchestrates speech synthesis by delegating to a configured ITTSBackend.

    All synthesis calls are dispatched to a thread-pool executor so the
    async event loop is never blocked by CPU-bound model inference.
    """

    def __init__(self, settings: Settings, language_service: LanguageService) -> None:
        self._settings = settings
        self._language_service = language_service
        self._backend: ITTSBackend = self._build_backend()
        logger.info(
            "TTSService ready – backend: %s, GPU: %s",
            type(self._backend).__name__,
            settings.TTS_USE_GPU,
        )

    # ── Public API ─────────────────────────────────────────────────────────────

    async def synthesize(self, text: str, language: str, voice_id: str | None = None) -> RawAudio:
        if not self._language_service.is_supported(language):
            raise ValueError(f"Unsupported language: '{language}'")

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            self._backend.synthesize,
            text,
            language,
            voice_id,
        )

    def is_language_ready(self, language: str) -> bool:
        return self._backend.is_ready(language)

    def get_backend_name(self) -> str:
        return type(self._backend).__name__

    def get_loaded_languages(self) -> list[str]:
        return [code for code in self._language_service.supported_codes() if self._backend.is_ready(code)]

    # ── Internals ──────────────────────────────────────────────────────────────

    def _build_backend(self) -> ITTSBackend:
        if self._settings.TTS_USE_XTTS:
            logger.info("Using XTTS v2 multilingual backend")
            return CoquiXTTSBackend(self._settings)
        logger.info("Using per-language single-speaker backend")
        return CoquiSingleSpeakerBackend(self._settings, self._language_service)
