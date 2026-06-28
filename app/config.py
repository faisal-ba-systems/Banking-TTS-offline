from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    APP_NAME: str = "Banking TTS Offline"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_V1_PREFIX: str = "/api/v1"

    # TTS Engine
    TTS_USE_GPU: bool = False
    TTS_USE_XTTS: bool = False
    TTS_XTTS_SPEAKER_WAV: str = ""
    TTS_MODELS_CACHE_DIR: str = "./tts_models_cache"

    # Per-language model names (Coqui TTS model IDs)
    TTS_MODEL_EN: str = "tts_models/en/ljspeech/tacotron2-DDC"
    TTS_MODEL_ES: str = "tts_models/es/mai/tacotron2-DDC"
    TTS_MODEL_AR: str = "tts_models/ar/cv/vits"
    TTS_MODEL_ZH: str = "tts_models/zh-CN/baker/tacotron2-DDC-GST"
    TTS_MODEL_JA: str = "tts_models/ja/kokoro/tacotron2-DDC"
    TTS_MODEL_FR: str = "tts_models/fr/mai/tacotron2-DDC"

    # Defaults
    DEFAULT_LANGUAGE: str = "en"

    def get_model_for_language(self, code: str) -> str:
        mapping = {
            "en": self.TTS_MODEL_EN,
            "es": self.TTS_MODEL_ES,
            "ar": self.TTS_MODEL_AR,
            "zh": self.TTS_MODEL_ZH,
            "ja": self.TTS_MODEL_JA,
            "fr": self.TTS_MODEL_FR,
        }
        return mapping.get(code, self.TTS_MODEL_EN)


@lru_cache
def get_settings() -> Settings:
    return Settings()
