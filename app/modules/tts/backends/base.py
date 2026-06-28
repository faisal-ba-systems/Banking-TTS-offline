from abc import ABC, abstractmethod
from dataclasses import dataclass


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
    def synthesize(self, text: str, language: str, voice_id: str | None = None) -> RawAudio:
        """Synthesize speech and return raw WAV bytes."""

    @abstractmethod
    def is_ready(self, language: str) -> bool:
        """Return True if the backend has a model loaded for the given language."""

    @abstractmethod
    def get_model_name(self, language: str) -> str:
        """Return the model identifier currently used for the given language."""
