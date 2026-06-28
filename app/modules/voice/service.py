import logging
from app.modules.voice.schemas import VoiceInfo

logger = logging.getLogger(__name__)

# ── Single-speaker registry (one model per language) ──────────────────────────
# voice_id here is a label only — these models have no speaker selection.
_SINGLE_SPEAKER_REGISTRY: dict[str, list[VoiceInfo]] = {
    "en": [VoiceInfo(voice_id="en_ljspeech", name="LJSpeech", language_code="en", gender="female", is_default=True, description="LJSpeech – clean, neutral American English")],
    "es": [VoiceInfo(voice_id="es_mai", name="MAI Spanish", language_code="es", gender="female", is_default=True)],
    "ar": [VoiceInfo(voice_id="ar_cv", name="Common Voice Arabic", language_code="ar", is_default=True)],
    "zh": [VoiceInfo(voice_id="zh_baker", name="Baker Chinese", language_code="zh", gender="female", is_default=True)],
    "ja": [VoiceInfo(voice_id="ja_kokoro", name="Kokoro Japanese", language_code="ja", is_default=True)],
    "fr": [VoiceInfo(voice_id="fr_mai", name="MAI French", language_code="fr", gender="female", is_default=True)],
}

# ── XTTS v2 built-in speakers ─────────────────────────────────────────────────
# voice_id MUST match the string in model.speakers exactly.
# All speakers are multilingual (work with every supported language).
_XTTS_VOICES: list[VoiceInfo] = [
    # Female
    VoiceInfo(voice_id="Claribel Dervla",    name="Claribel Dervla",    language_code="multilingual", gender="female", is_default=True),
    VoiceInfo(voice_id="Daisy Studious",     name="Daisy Studious",     language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Gracie Wise",        name="Gracie Wise",        language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Tammie Ema",         name="Tammie Ema",         language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Alison Dietlinde",   name="Alison Dietlinde",   language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Ana Florence",       name="Ana Florence",       language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Annmarie Nele",      name="Annmarie Nele",      language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Asya Anara",         name="Asya Anara",         language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Brenda Stern",       name="Brenda Stern",       language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Gitta Nikolina",     name="Gitta Nikolina",     language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Henriette Usha",     name="Henriette Usha",     language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Sofia Hellen",       name="Sofia Hellen",       language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Tammy Grit",         name="Tammy Grit",         language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Tanja Adelina",      name="Tanja Adelina",      language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Vjollca Johnnie",    name="Vjollca Johnnie",    language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Nova Hogarth",       name="Nova Hogarth",       language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Maja Ruoho",         name="Maja Ruoho",         language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Uta Obando",         name="Uta Obando",         language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Lidiya Szekeres",    name="Lidiya Szekeres",    language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Chandra MacFarland", name="Chandra MacFarland", language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Szofi Granger",      name="Szofi Granger",      language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Camilla Holmström",  name="Camilla Holmström",  language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Lilya Stainthorpe",  name="Lilya Stainthorpe",  language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Zofija Kendrick",    name="Zofija Kendrick",    language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Narelle Moon",       name="Narelle Moon",       language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Barbora MacLean",    name="Barbora MacLean",    language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Alexandra Hisakawa", name="Alexandra Hisakawa", language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Alma María",         name="Alma María",         language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Rosemarie Bhatt",    name="Rosemarie Bhatt",    language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Ige Behringer",      name="Ige Behringer",      language_code="multilingual", gender="female"),
    VoiceInfo(voice_id="Eunice Solberg",     name="Eunice Solberg",     language_code="multilingual", gender="female"),
    # Male
    VoiceInfo(voice_id="Andrew Chipper",     name="Andrew Chipper",     language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Badr Odhiambo",      name="Badr Odhiambo",      language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Dionisio Schuyler",  name="Dionisio Schuyler",  language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Royston Min",        name="Royston Min",        language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Viktor Eka",         name="Viktor Eka",         language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Abrahan Mack",       name="Abrahan Mack",       language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Adde Michal",        name="Adde Michal",        language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Baldur Sanjin",      name="Baldur Sanjin",      language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Craig Gutsy",        name="Craig Gutsy",        language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Damien Black",       name="Damien Black",       language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Gilberto Mathias",   name="Gilberto Mathias",   language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Ilkin Urbano",       name="Ilkin Urbano",       language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Kazuhiko Atallah",   name="Kazuhiko Atallah",   language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Ludvig Milivoj",     name="Ludvig Milivoj",     language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Suad Qasim",         name="Suad Qasim",         language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Torcull Diarmuid",   name="Torcull Diarmuid",   language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Viktor Menelaos",    name="Viktor Menelaos",    language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Zacharie Aimilios",  name="Zacharie Aimilios",  language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Filip Traverse",     name="Filip Traverse",     language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Damjan Chapman",     name="Damjan Chapman",     language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Wulf Carlevaro",     name="Wulf Carlevaro",     language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Aaron Dreschner",    name="Aaron Dreschner",    language_code="multilingual", gender="male"),
    VoiceInfo(voice_id="Kumar Dahl",         name="Kumar Dahl",         language_code="multilingual", gender="male"),
]


class VoiceService:
    """Returns available TTS voices, grouped by language."""

    def list_voices(self, language_code: str | None = None) -> list[VoiceInfo]:
        """Single-speaker backend: one voice per language."""
        if language_code:
            return _SINGLE_SPEAKER_REGISTRY.get(language_code, [])
        return [v for voices in _SINGLE_SPEAKER_REGISTRY.values() for v in voices]

    def list_xtts_voices(self, gender: str | None = None) -> list[VoiceInfo]:
        """XTTS v2 backend: all multilingual built-in speakers."""
        if gender:
            return [v for v in _XTTS_VOICES if v.gender == gender.lower()]
        return list(_XTTS_VOICES)

    def get_default_voice(self, language_code: str) -> VoiceInfo | None:
        voices = _SINGLE_SPEAKER_REGISTRY.get(language_code, [])
        return next((v for v in voices if v.is_default), voices[0] if voices else None)

    def supported_language_codes(self) -> list[str]:
        return list(_SINGLE_SPEAKER_REGISTRY.keys())
