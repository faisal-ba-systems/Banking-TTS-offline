from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from app.modules.tts.schemas import ProsodySettings


@dataclass
class RawAudio:
    """Raw synthesis result before encoding to a file format."""
    wav_bytes: bytes       # PCM-16 WAV
    sample_rate: int
    duration_seconds: float
    language: str
    model_name: str


class ITTSBackend(ABC):
    """
    Abstract contract for a TTS synthesis backend.

    Implementors must be thread-safe: FastAPI may call synthesize() concurrently
    from multiple worker threads via run_in_executor.
    """

    @abstractmethod
    def synthesize(self, text: str, language: str, prosody: ProsodySettings | None = None) -> RawAudio:
        """Synthesize speech and return raw WAV bytes."""

    @abstractmethod
    def is_ready(self, language: str) -> bool:
        """Return True if the backend has a model loaded for the given language."""

    @abstractmethod
    def get_model_name(self, language: str) -> str:
        """Return the model identifier currently used for the given language."""

    # ── Post-processing helpers ────────────────────────────────────────────────

    @staticmethod
    def _apply_prosody(
        audio: np.ndarray,
        sample_rate: int,
        prosody: ProsodySettings,
        apply_speed: bool = True,
    ) -> np.ndarray:
        """
        Apply prosody transformations to a float32 audio array in-place order:
          1. Speed  — time-stretch (changes duration, not pitch)
          2. Pitch  — double-resample (preserves duration)
          3. Volume — amplitude scale

        Set apply_speed=False when the backend already passed speed to the
        model natively (e.g. XTTS) to avoid double-applying it.
        """
        if apply_speed and abs(prosody.speed - 1.0) > 1e-6:
            n_new = max(1, round(len(audio) / prosody.speed))
            audio = ITTSBackend._resample(audio, n_new)

        if abs(prosody.pitch) > 1e-6:
            factor = 2.0 ** (prosody.pitch / 12.0)
            n_original = len(audio)
            # Shift pitch: resample to n/factor (pitch changes), then back to n (restore duration)
            audio = ITTSBackend._resample(audio, max(1, round(n_original / factor)))
            audio = ITTSBackend._resample(audio, n_original)

        if abs(prosody.volume - 1.0) > 1e-6:
            audio = np.clip(audio * prosody.volume, -1.0, 1.0)

        return audio

    @staticmethod
    def _resample(audio: np.ndarray, new_length: int) -> np.ndarray:
        """Linear-interpolation resampling — no extra dependencies beyond numpy."""
        if new_length == len(audio) or len(audio) == 0:
            return audio
        x_old = np.linspace(0.0, 1.0, len(audio))
        x_new = np.linspace(0.0, 1.0, new_length)
        return np.interp(x_new, x_old, audio).astype(np.float32)
