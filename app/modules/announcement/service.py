import logging
from dataclasses import dataclass

from app.modules.language.schemas import LanguageConfig
from app.modules.language.service import LanguageService
from app.modules.tts.backends.base import RawAudio
from app.modules.tts.schemas import ProsodySettings
from app.modules.tts.service import TTSService

logger = logging.getLogger(__name__)


@dataclass
class AnnouncementResult:
    announcement_text: str
    audio: RawAudio


class AnnouncementService:
    """
    Converts a structured announcement request into spoken audio.

    Responsibilities:
      1. Expand alphanumeric tokens digit-by-digit (e.g. "A13" → "A one three").
      2. Render the language-specific announcement template.
      3. Delegate to TTSService for audio synthesis.
    """

    def __init__(self, tts_service: TTSService, language_service: LanguageService) -> None:
        self._tts = tts_service
        self._language_service = language_service

    async def synthesize(
        self,
        token_number: str,
        counter_number: str,
        language: str,
        prosody: ProsodySettings | None = None,
    ) -> AnnouncementResult:
        lang_config = self._language_service.get(language)
        text = self._build_announcement_text(token_number, counter_number, lang_config)
        logger.info("Announcing [%s] token='%s' counter='%s' → '%s'", language, token_number, counter_number, text)
        audio = await self._tts.synthesize(text, language, prosody)
        return AnnouncementResult(announcement_text=text, audio=audio)

    def build_preview_text(
        self,
        token_number: str,
        counter_number: str,
        language: str,
    ) -> str:
        lang_config = self._language_service.get(language)
        return self._build_announcement_text(token_number, counter_number, lang_config)

    # ── Internals ──────────────────────────────────────────────────────────────

    def _build_announcement_text(
        self,
        token_number: str,
        counter_number: str,
        lang: LanguageConfig,
    ) -> str:
        expanded_token = self._expand_alphanumeric(token_number, lang.digit_words)
        expanded_counter = self._expand_alphanumeric(counter_number, lang.digit_words)
        return lang.announcement_template.format(token=expanded_token, counter=expanded_counter)

    @staticmethod
    def _expand_alphanumeric(text: str, digit_words: dict[str, str]) -> str:
        """
        Expand each character of *text* into its spoken form:
          - Digit  → word from digit_words  (e.g. '1' → 'one')
          - Letter → kept as the uppercase letter (TTS reads it phonetically)

        A comma is appended to a letter when the next character is a digit so
        the TTS engine inserts a brief pause between the prefix letter and the
        digit sequence (e.g. 'B13' → 'B, one three').

        Examples (English):
          'B13'  → 'B, one three'
          'A13'  → 'A, one three'
          '105'  → 'one zero five'
          '23'   → 'two three'
        """
        parts: list[str] = []
        prev_was_letter = False
        for char in text.upper():
            if char.isdigit():
                if prev_was_letter and parts:
                    parts[-1] += ","
                parts.append(digit_words[char])
                prev_was_letter = False
            elif char.isalpha():
                parts.append(char)
                prev_was_letter = True
            # Non-alphanumeric characters (e.g. '-') are silently skipped.
        return " ".join(parts)
