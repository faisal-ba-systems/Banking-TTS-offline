import logging
from app.modules.voice.schemas import VoiceInfo

logger = logging.getLogger(__name__)

# Default single-speaker voice for each language (backed by single-speaker Coqui models).
# When TTS_USE_XTTS is enabled, the XTTS backend exposes its own built-in speakers
# through this same registry.
_VOICE_REGISTRY: dict[str, list[VoiceInfo]] = {
    "en": [VoiceInfo(voice_id="en_ljspeech", name="LJSpeech", language_code="en", gender="female", is_default=True, description="LJSpeech – clean, neutral American English")],
    "es": [VoiceInfo(voice_id="es_mai", name="MAI Spanish", language_code="es", gender="female", is_default=True)],
    "ar": [VoiceInfo(voice_id="ar_cv", name="Common Voice Arabic", language_code="ar", is_default=True)],
    "zh": [VoiceInfo(voice_id="zh_baker", name="Baker Chinese", language_code="zh", gender="female", is_default=True)],
    "ja": [VoiceInfo(voice_id="ja_kokoro", name="Kokoro Japanese", language_code="ja", is_default=True)],
    "fr": [VoiceInfo(voice_id="fr_mai", name="MAI French", language_code="fr", gender="female", is_default=True)],
}


class VoiceService:
    """Returns available TTS voices, grouped by language."""

    def list_voices(self, language_code: str | None = None) -> list[VoiceInfo]:
        if language_code:
            return _VOICE_REGISTRY.get(language_code, [])
        return [v for voices in _VOICE_REGISTRY.values() for v in voices]

    def get_default_voice(self, language_code: str) -> VoiceInfo | None:
        voices = _VOICE_REGISTRY.get(language_code, [])
        return next((v for v in voices if v.is_default), voices[0] if voices else None)

    def supported_language_codes(self) -> list[str]:
        return list(_VOICE_REGISTRY.keys())
