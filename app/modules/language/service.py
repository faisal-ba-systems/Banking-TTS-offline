import logging
from app.config import Settings
from app.modules.language.schemas import LanguageConfig

logger = logging.getLogger(__name__)

# ── Language Registry ─────────────────────────────────────────────────────────
# The announcement_template must contain {token} and {counter} placeholders.
# digit_words maps "0"-"9" to the spoken word in the target language.

_LANGUAGE_REGISTRY: dict[str, LanguageConfig] = {
    "en": LanguageConfig(
        code="en",
        name="English",
        native_name="English",
        tts_model="tts_models/en/ljspeech/tacotron2-DDC",
        digit_words={
            "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
            "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine",
        },
        announcement_template="Token number, {token}, counter number, {counter}.",
    ),
    "es": LanguageConfig(
        code="es",
        name="Spanish",
        native_name="Español",
        tts_model="tts_models/es/mai/tacotron2-DDC",
        digit_words={
            "0": "cero", "1": "uno", "2": "dos", "3": "tres", "4": "cuatro",
            "5": "cinco", "6": "seis", "7": "siete", "8": "ocho", "9": "nueve",
        },
        announcement_template="Número de ficha {token}, número de ventanilla {counter}.",
    ),
    "ar": LanguageConfig(
        code="ar",
        name="Arabic",
        native_name="العربية",
        tts_model="tts_models/ar/cv/vits",
        digit_words={
            "0": "صفر", "1": "واحد", "2": "اثنان", "3": "ثلاثة", "4": "أربعة",
            "5": "خمسة", "6": "ستة", "7": "سبعة", "8": "ثمانية", "9": "تسعة",
        },
        announcement_template="رقم التذكرة {token}، رقم الشباك {counter}.",
    ),
    "zh": LanguageConfig(
        code="zh",
        name="Chinese",
        native_name="中文",
        tts_model="tts_models/zh-CN/baker/tacotron2-DDC-GST",
        digit_words={
            "0": "零", "1": "一", "2": "二", "3": "三", "4": "四",
            "5": "五", "6": "六", "7": "七", "8": "八", "9": "九",
        },
        announcement_template="号码牌{token}，柜台{counter}。",
    ),
    "ja": LanguageConfig(
        code="ja",
        name="Japanese",
        native_name="日本語",
        tts_model="tts_models/ja/kokoro/tacotron2-DDC",
        digit_words={
            "0": "ゼロ", "1": "いち", "2": "に", "3": "さん", "4": "し",
            "5": "ご", "6": "ろく", "7": "なな", "8": "はち", "9": "きゅう",
        },
        announcement_template="トークン番号{token}、カウンター番号{counter}。",
    ),
    "fr": LanguageConfig(
        code="fr",
        name="French",
        native_name="Français",
        tts_model="tts_models/fr/mai/tacotron2-DDC",
        digit_words={
            "0": "zéro", "1": "un", "2": "deux", "3": "trois", "4": "quatre",
            "5": "cinq", "6": "six", "7": "sept", "8": "huit", "9": "neuf",
        },
        announcement_template="Numéro de jeton {token}, numéro de guichet {counter}.",
    ),
}


class LanguageService:
    """Manages the registry of supported languages and their TTS configurations."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        # Apply model overrides from settings so env vars take precedence
        self._registry = self._apply_model_overrides(_LANGUAGE_REGISTRY)
        logger.info("LanguageService initialized with %d languages", len(self._registry))

    def _apply_model_overrides(self, registry: dict[str, LanguageConfig]) -> dict[str, LanguageConfig]:
        updated: dict[str, LanguageConfig] = {}
        for code, config in registry.items():
            override = self._settings.get_model_for_language(code)
            updated[code] = config.model_copy(update={"tts_model": override})
        return updated

    def is_supported(self, code: str) -> bool:
        return code in self._registry

    def get(self, code: str) -> LanguageConfig:
        if not self.is_supported(code):
            raise ValueError(f"Unsupported language code: '{code}'. Supported: {self.supported_codes()}")
        return self._registry[code]

    def list_all(self) -> list[LanguageConfig]:
        return list(self._registry.values())

    def supported_codes(self) -> list[str]:
        return list(self._registry.keys())
