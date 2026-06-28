from pydantic import BaseModel, Field


class DigitWordMap(BaseModel):
    """Maps digit characters 0-9 to their spoken word in a given language."""
    zero: str
    one: str
    two: str
    three: str
    four: str
    five: str
    six: str
    seven: str
    eight: str
    nine: str

    def to_dict(self) -> dict[str, str]:
        return {
            "0": self.zero, "1": self.one, "2": self.two,
            "3": self.three, "4": self.four, "5": self.five,
            "6": self.six, "7": self.seven, "8": self.eight,
            "9": self.nine,
        }


class LanguageConfig(BaseModel):
    """Full configuration for a supported language."""
    code: str = Field(description="ISO 639-1 language code")
    name: str = Field(description="Language name in English")
    native_name: str = Field(description="Language name in its own script")
    tts_model: str = Field(description="Default Coqui TTS model ID for this language")
    digit_words: dict[str, str] = Field(description="Digit → spoken word mapping")
    # {token} and {counter} are substituted with the expanded alphanumeric strings
    announcement_template: str = Field(description="Announcement text template")


class LanguageListResponse(BaseModel):
    languages: list[LanguageConfig]
    total: int


class LanguageDetailResponse(LanguageConfig):
    pass
