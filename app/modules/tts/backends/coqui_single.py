import io
import logging
import threading
import time

import numpy as np
import soundfile as sf

from app.config import Settings
from app.modules.language.service import LanguageService
from app.modules.tts.backends.base import ITTSBackend, RawAudio
from app.modules.tts.schemas import ProsodySettings

logger = logging.getLogger(__name__)

_DEFAULT_PROSODY = ProsodySettings()


class CoquiSingleSpeakerBackend(ITTSBackend):
    """
    Loads one language-specific Coqui TTS single-speaker model per language.

    Models are loaded lazily on first use and kept in memory for the lifetime
    of the process.  A per-language lock prevents duplicate loading under
    concurrent first requests.

    Prosody (speed, pitch, volume) is applied via post-processing so it works
    uniformly across all single-speaker model architectures.
    """

    def __init__(self, settings: Settings, language_service: LanguageService) -> None:
        self._settings = settings
        self._language_service = language_service
        self._models: dict[str, object] = {}          # language → TTS instance
        self._locks: dict[str, threading.Lock] = {}   # language → load lock

    # ── Public API ─────────────────────────────────────────────────────────────

    def synthesize(self, text: str, language: str, prosody: ProsodySettings | None = None) -> RawAudio:
        _prosody = prosody or _DEFAULT_PROSODY
        model = self._get_model(language)
        lang_config = self._language_service.get(language)

        logger.debug("Synthesizing %d chars in '%s' using %s", len(text), language, lang_config.tts_model)
        t0 = time.perf_counter()

        wav_array = model.tts(text)
        sample_rate: int = model.synthesizer.output_sample_rate
        duration = time.perf_counter() - t0

        audio = self._apply_prosody(np.array(wav_array, dtype=np.float32), sample_rate, _prosody, apply_speed=True)
        audio_duration = len(audio) / sample_rate

        wav_bytes = self._array_to_wav(audio, sample_rate)
        logger.info("Synthesized %.2fs audio in %.2fs for language '%s'", audio_duration, duration, language)
        return RawAudio(
            wav_bytes=wav_bytes,
            sample_rate=sample_rate,
            duration_seconds=audio_duration,
            language=language,
            model_name=lang_config.tts_model,
        )

    def is_ready(self, language: str) -> bool:
        return language in self._models

    def get_model_name(self, language: str) -> str:
        return self._language_service.get(language).tts_model

    # ── Internals ──────────────────────────────────────────────────────────────

    def _get_model(self, language: str) -> object:
        if language not in self._models:
            lock = self._locks.setdefault(language, threading.Lock())
            with lock:
                if language not in self._models:
                    self._models[language] = self._load_model(language)
        return self._models[language]

    def _load_model(self, language: str) -> object:
        # Import here so the heavy Coqui TTS package only loads when needed.
        from TTS.api import TTS  # type: ignore[import]

        lang_config = self._language_service.get(language)
        model_name = lang_config.tts_model
        logger.info("Loading TTS model '%s' for language '%s'…", model_name, language)
        t0 = time.perf_counter()

        model = TTS(model_name=model_name, gpu=self._settings.TTS_USE_GPU)

        logger.info("Model '%s' loaded in %.1fs", model_name, time.perf_counter() - t0)
        return model

    @staticmethod
    def _array_to_wav(audio: np.ndarray, sample_rate: int) -> bytes:
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format="WAV", subtype="PCM_16")
        buffer.seek(0)
        return buffer.read()
