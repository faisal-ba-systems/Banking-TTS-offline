import io
import logging
import threading
import time

import numpy as np
import soundfile as sf

from app.config import Settings
from app.modules.tts.backends.base import ITTSBackend, RawAudio

logger = logging.getLogger(__name__)

XTTS_MODEL_ID = "tts_models/multilingual/multi-dataset/xtts_v2"

# Maps our ISO 639-1 codes to the language tag expected by XTTS v2.
_XTTS_LANG_MAP: dict[str, str] = {
    "en": "en",
    "es": "es",
    "ar": "ar",
    "zh": "zh-cn",
    "ja": "ja",
    "fr": "fr",
}


class CoquiXTTSBackend(ITTSBackend):
    """
    Uses the multilingual Coqui XTTS v2 model for all languages.

    Requires either:
      - A speaker WAV file (TTS_XTTS_SPEAKER_WAV env var) for voice cloning.
      - Or a built-in speaker name (first available speaker used by default).
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._model: object | None = None
        self._lock = threading.Lock()

    # ── Public API ─────────────────────────────────────────────────────────────

    def synthesize(self, text: str, language: str, voice_id: str | None = None) -> RawAudio:
        model = self._get_model()
        xtts_lang = _XTTS_LANG_MAP.get(language, language)

        kwargs: dict = {"text": text, "language": xtts_lang}

        speaker_wav = self._settings.TTS_XTTS_SPEAKER_WAV
        if speaker_wav:
            kwargs["speaker_wav"] = speaker_wav
        else:
            # Fall back to the first built-in speaker when no reference wav is configured.
            speakers: list[str] = getattr(model, "speakers", None) or []
            if speakers:
                kwargs["speaker"] = voice_id if voice_id in speakers else speakers[0]
            else:
                raise RuntimeError(
                    "XTTS v2 requires either TTS_XTTS_SPEAKER_WAV to be set "
                    "or a model that exposes built-in speakers."
                )

        logger.debug("XTTS synthesizing %d chars in '%s'", len(text), language)
        t0 = time.perf_counter()

        wav_array = model.tts(**kwargs)
        sample_rate: int = model.synthesizer.output_sample_rate
        duration = time.perf_counter() - t0

        wav_bytes = self._array_to_wav(np.array(wav_array, dtype=np.float32), sample_rate)
        audio_duration = len(wav_array) / sample_rate

        logger.info("XTTS synthesized %.2fs audio in %.2fs", audio_duration, duration)
        return RawAudio(
            wav_bytes=wav_bytes,
            sample_rate=sample_rate,
            duration_seconds=audio_duration,
            language=language,
            model_name=XTTS_MODEL_ID,
        )

    def is_ready(self, language: str) -> bool:
        return self._model is not None and language in _XTTS_LANG_MAP

    def get_model_name(self, language: str) -> str:
        return XTTS_MODEL_ID

    # ── Internals ──────────────────────────────────────────────────────────────

    def _get_model(self) -> object:
        if self._model is None:
            with self._lock:
                if self._model is None:
                    self._model = self._load_model()
        return self._model

    def _load_model(self) -> object:
        from TTS.api import TTS  # type: ignore[import]

        logger.info("Loading XTTS v2 multilingual model…")
        t0 = time.perf_counter()
        model = TTS(model_name=XTTS_MODEL_ID, gpu=self._settings.TTS_USE_GPU)
        logger.info("XTTS v2 loaded in %.1fs", time.perf_counter() - t0)
        return model

    @staticmethod
    def _array_to_wav(audio: np.ndarray, sample_rate: int) -> bytes:
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format="WAV", subtype="PCM_16")
        buffer.seek(0)
        return buffer.read()
