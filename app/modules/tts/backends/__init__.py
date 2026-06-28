from app.modules.tts.backends.base import ITTSBackend, RawAudio
from app.modules.tts.backends.coqui_single import CoquiSingleSpeakerBackend
from app.modules.tts.backends.coqui_xtts import CoquiXTTSBackend

__all__ = ["ITTSBackend", "RawAudio", "CoquiSingleSpeakerBackend", "CoquiXTTSBackend"]
