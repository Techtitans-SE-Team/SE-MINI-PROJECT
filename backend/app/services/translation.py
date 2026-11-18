"""Medication instruction translation (Google Translate via deep-translator) with proper error handling.

The old failure mode was an unhandled "TooManyRequests" crashing the request. Now:
  1. calls are spaced + retried with backoff (see external.ServiceGuard),
  2. after repeated 429s the service is paused for a cool-down instead of being hammered,
  3. results are cached, so the same text/language is never requested twice,
  4. if translation is still impossible the caller gets the ENGLISH text with translated=False and a warning
     (a patient must never receive a wrong or empty instruction),
  5. medicine name and dosage numbers are verified to survive translation.
"""
import re
from dataclasses import dataclass

from .external import RATE_LIMITED, TRANSIENT, ServiceGuard, ServiceUnavailable
from .languages import Language

guard = ServiceGuard("Google Translate")
_cache: dict[tuple[str, str], str] = {}


@dataclass
class TranslationResult:
    text: str
    language: str
    translated: bool
    warning: str | None = None


def build_instruction_text(medicine_name: str, dosage: str, frequency: str, duration: str,
                           instructions: str | None = None) -> str:
    text = f"Take {medicine_name}, {dosage}, {frequency}, for {duration}."
    if instructions and instructions.strip():
        text += f" {instructions.strip().rstrip('.')}."
    return text


def _classify(exc: Exception) -> str | None:
    from deep_translator.exceptions import RequestError, ServerException, TooManyRequests
    import requests
    if isinstance(exc, TooManyRequests):
        return RATE_LIMITED
    if isinstance(exc, (RequestError, ServerException, requests.exceptions.RequestException)):
        return TRANSIENT
    return None


def _google(text: str, code: str) -> str:
    from deep_translator import GoogleTranslator
    return GoogleTranslator(source="en", target=code).translate(text)


def _keeps_critical_details(original_name: str | None, original_dosage: str | None, translated: str) -> bool:
    low = translated.lower()
    if original_name and original_name.lower() not in low:
        return False
    return all(n in translated for n in re.findall(r"\d+(?:\.\d+)?", original_dosage or ""))


def translate_instruction(text: str, language: Language, *, medicine_name: str | None = None,
                          dosage: str | None = None) -> TranslationResult:
    if language.code == "en":
        return TranslationResult(text, "en", True)
    key = (text, language.code)
    if key in _cache:
        return TranslationResult(_cache[key], language.code, True)
    try:
        out = guard.call(lambda: _google(text, language.code), _classify)
    except ServiceUnavailable as exc:
        return TranslationResult(text, "en", False, f"{exc}. Showing English instead")
    except Exception as exc:  # unsupported language, empty result, parsing problems...
        return TranslationResult(text, "en", False, f"Translation failed ({exc.__class__.__name__}). Showing English instead")
    if not out or not out.strip():
        return TranslationResult(text, "en", False, "Translation returned no text. Showing English instead")
    if not _keeps_critical_details(medicine_name, dosage, out):
        # keep the safety-critical facts in Latin script next to the translation
        out = f"{out} ({medicine_name}, {dosage})"
    _cache[key] = out
    return TranslationResult(out, language.code, True)
