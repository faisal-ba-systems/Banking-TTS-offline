import io
import logging
import threading
import time

import numpy as np
import soundfile as sf

from app.config import Settings
from app.modules.tts.backends.base import ITTSBackend, RawAudio
from app.modules.tts.schemas import ProsodySettings

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

_DEFAULT_PROSODY = ProsodySettings()


class CoquiXTTSBackend(ITTSBackend):
    """
    Uses the multilingual Coqui XTTS v2 model for all languages.

    Requires either:
      - A speaker WAV file (TTS_XTTS_SPEAKER_WAV env var) for voice cloning.
      - Or a built-in speaker name (first available speaker used by default).

    Speed is passed natively to XTTS; pitch and volume are applied via
    post-processing so they work regardless of XTTS version.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._model: object | None = None
        self._lock = threading.Lock()

    # ── Public API ─────────────────────────────────────────────────────────────

    def synthesize(self, text: str, language: str, prosody: ProsodySettings | None = None) -> RawAudio:
        _prosody = prosody or _DEFAULT_PROSODY
        model = self._get_model()
        xtts_lang = _XTTS_LANG_MAP.get(language, language)

        kwargs: dict = {
            "text": text,
            "language": xtts_lang,
            "speed": _prosody.speed,
        }

        speaker_wav = self._settings.TTS_XTTS_SPEAKER_WAV
        if speaker_wav:
            kwargs["speaker_wav"] = speaker_wav
        else:
            speakers: list[str] = getattr(model, "speakers", None) or []
            if speakers:
                chosen = _prosody.voice_id if _prosody.voice_id in speakers else speakers[0]
                kwargs["speaker"] = chosen
            else:
                raise RuntimeError(
                    "XTTS v2 requires either TTS_XTTS_SPEAKER_WAV to be set "
                    "or a model that exposes built-in speakers."
                )

        kwargs["text"] = self._prepare_text(kwargs["text"])
        logger.debug("XTTS synthesizing %d chars in '%s' (speed=%.2f)", len(kwargs["text"]), language, _prosody.speed)
        t0 = time.perf_counter()

        wav_array = model.tts(**kwargs)
        sample_rate: int = model.synthesizer.output_sample_rate
        duration = time.perf_counter() - t0

        # Speed is already applied natively; only apply pitch and volume here.
        audio = self._apply_prosody(
            np.array(wav_array, dtype=np.float32), sample_rate, _prosody, apply_speed=False
        )
        audio = self._trim_and_fade(audio, sample_rate)
        audio_duration = len(audio) / sample_rate

        wav_bytes = self._array_to_wav(audio, sample_rate)
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
    def _prepare_text(text: str) -> str:
        """
        Guard against XTTS hallucinating extra words after the sentence ends.

        XTTS v2 sometimes continues generating speech past the final period
        (e.g. "five. at all").  A second stop marker — a space followed by
        another period — gives the model a clear double boundary and reliably
        suppresses this behaviour.
        """
        text = text.strip()
        if not text:
            return text
        # Ensure there is already a hard stop at the end
        if text[-1] not in ".!?。！？،":
            text += "."
        # Append the hallucination-suppressor
        return text + " ."

    @staticmethod
    def _array_to_wav(audio: np.ndarray, sample_rate: int) -> bytes:
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format="WAV", subtype="PCM_16")
        buffer.seek(0)
        return buffer.read()
