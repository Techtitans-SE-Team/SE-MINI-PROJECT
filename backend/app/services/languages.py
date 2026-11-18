"""Supported Indian languages (+ English). Patients store the language as free text, so resolve names AND codes."""
from dataclasses import dataclass
from pathlib import Path

FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"


@dataclass(frozen=True)
class Language:
    name: str
    code: str
    font: str


LANGUAGES = [
    Language("English", "en", "NotoSans-Regular.ttf"),
    Language("Hindi", "hi", "NotoSansDevanagari-Regular.ttf"),
    Language("Marathi", "mr", "NotoSansDevanagari-Regular.ttf"),
    Language("Kannada", "kn", "NotoSansKannada-Regular.ttf"),
    Language("Tamil", "ta", "NotoSansTamil-Regular.ttf"),
    Language("Telugu", "te", "NotoSansTelugu-Regular.ttf"),
    Language("Malayalam", "ml", "NotoSansMalayalam-Regular.ttf"),
    Language("Bengali", "bn", "NotoSansBengali-Regular.ttf"),
    Language("Gujarati", "gu", "NotoSansGujarati-Regular.ttf"),
    Language("Punjabi", "pa", "NotoSansGurmukhi-Regular.ttf"),
]
_BY_KEY = {k: lang for lang in LANGUAGES for k in (lang.name.lower(), lang.code)}


def resolve_language(value: str | None) -> Language | None:
    return _BY_KEY.get((value or "").strip().lower())


def supported_names() -> list[str]:
    return [lang.name for lang in LANGUAGES]
