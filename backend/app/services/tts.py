"""Text-to-speech (Google TTS via gTTS) with the same retry / rate-limit protection as translation."""
from pathlib import Path

from .external import RATE_LIMITED, TRANSIENT, ServiceGuard, ServiceUnavailable

guard = ServiceGuard("Google Text-to-Speech")


class TTSError(Exception):
    pass


def _classify(exc: Exception) -> str | None:
    from gtts import gTTSError
    import requests
    if isinstance(exc, gTTSError):
        status = getattr(getattr(exc, "rsp", None), "status_code", None)
        return RATE_LIMITED if status == 429 or "429" in str(exc) else TRANSIENT
    if isinstance(exc, requests.exceptions.RequestException):
        return TRANSIENT
    return None


def is_supported(code: str) -> bool:
    from gtts.lang import tts_langs
    return code in tts_langs()


def _synthesize(text: str, code: str, out_path: Path) -> None:
    from gtts import gTTS
    gTTS(text=text, lang=code).save(str(out_path))


def synthesize(text: str, code: str, out_path: Path) -> Path:
    """Write an MP3 to out_path. Raises TTSError with a user-presentable message."""
    if not is_supported(code):
        raise TTSError(f"Audio is not available for language code '{code}'")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        guard.call(lambda: _synthesize(text, code, out_path), _classify)
    except ServiceUnavailable as exc:
        raise TTSError(str(exc)) from exc
    except Exception as exc:
        raise TTSError(f"Audio generation failed ({exc.__class__.__name__})") from exc
    if not out_path.exists() or out_path.stat().st_size == 0:
        raise TTSError("Audio generation produced an empty file")
    return out_path
