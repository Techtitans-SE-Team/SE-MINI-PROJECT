"""Translation / TTS error handling (the Google 'TooManyRequests' problem) - all external calls are mocked."""
import pytest
from deep_translator.exceptions import TooManyRequests
from gtts import gTTSError

from app.services import external, translation, tts
from app.services.languages import resolve_language

KN = resolve_language("Kannada")


@pytest.fixture(autouse=True)
def clean():
    translation._cache.clear()
    translation.guard.reset()
    tts.guard.reset()
    yield


def test_language_resolution_accepts_names_and_codes():
    assert resolve_language("kannada").code == "kn"
    assert resolve_language(" HI ").name == "Hindi"
    assert resolve_language("Klingon") is None and resolve_language(None) is None


def test_english_needs_no_external_call(monkeypatch):
    monkeypatch.setattr(translation, "_google", lambda *a: pytest.fail("must not be called"))
    r = translation.translate_instruction("Take X", resolve_language("en"))
    assert r.translated and r.text == "Take X"


def test_rate_limit_is_retried_then_succeeds(monkeypatch):
    calls = []

    def flaky(text, code):
        calls.append(code)
        if len(calls) < 3:
            raise TooManyRequests()
        return "ಪ್ಯಾರಾಸಿಟಮಾಲ್ Paracetamol 500 mg"
    monkeypatch.setattr(translation, "_google", flaky)
    r = translation.translate_instruction("Take Paracetamol, 500 mg", KN, medicine_name="Paracetamol", dosage="500 mg")
    assert r.translated and len(calls) == 3 and r.warning is None


def test_persistent_rate_limit_falls_back_to_english_and_pauses_service(monkeypatch):
    calls = []

    def always(text, code):
        calls.append(1)
        raise TooManyRequests()
    monkeypatch.setattr(translation, "_google", always)
    r = translation.translate_instruction("Take Paracetamol, 500 mg", KN)
    assert not r.translated and r.text == "Take Paracetamol, 500 mg" and "rate limited" in r.warning
    n = len(calls)
    assert n == 4                      # 1 try + 3 retries, no crash
    r2 = translation.translate_instruction("Take Other, 5 ml", KN)   # cool-down: Google is not hit again
    assert not r2.translated and len(calls) == n


def test_unexpected_error_does_not_crash(monkeypatch):
    def boom(text, code):
        raise ValueError("weird")
    monkeypatch.setattr(translation, "_google", boom)
    r = translation.translate_instruction("Take X, 1 mg", KN)
    assert not r.translated and "English" in r.warning


def test_empty_translation_falls_back(monkeypatch):
    monkeypatch.setattr(translation, "_google", lambda t, c: "  ")
    assert not translation.translate_instruction("Take X, 1 mg", KN).translated


def test_dosage_and_name_are_preserved(monkeypatch):
    monkeypatch.setattr(translation, "_google", lambda t, c: "ಮಾತ್ರೆ ತೆಗೆದುಕೊಳ್ಳಿ")   # lost name + dosage
    r = translation.translate_instruction("Take Amoxil, 250 mg", KN, medicine_name="Amoxil", dosage="250 mg")
    assert "Amoxil" in r.text and "250 mg" in r.text


def test_results_are_cached(monkeypatch):
    n = []
    monkeypatch.setattr(translation, "_google", lambda t, c: n.append(1) or "ok Amoxil 250")
    for _ in range(3):
        translation.translate_instruction("Take Amoxil, 250 mg", KN, medicine_name="Amoxil", dosage="250 mg")
    assert len(n) == 1


def test_tts_rate_limit_raises_clean_error(monkeypatch):
    def limited(text, code, path):
        raise gTTSError("429 (Too Many Requests) from TTS API")
    monkeypatch.setattr(tts, "_synthesize", limited)
    with pytest.raises(tts.TTSError, match="rate limited"):
        tts.synthesize("hello", "kn", __import__("pathlib").Path("/tmp/x.mp3"))


def test_tts_success_and_unsupported_language(monkeypatch, tmp_path):
    monkeypatch.setattr(tts, "_synthesize", lambda t, c, p: p.write_bytes(b"ID3data"))
    assert tts.synthesize("hi", "hi", tmp_path / "a.mp3").exists()
    with pytest.raises(tts.TTSError):
        tts.synthesize("hi", "xx", tmp_path / "b.mp3")


def test_guard_does_not_retry_non_retryable():
    g = external.ServiceGuard("t")
    n = []

    def f():
        n.append(1)
        raise KeyError("x")
    with pytest.raises(KeyError):
        g.call(f, lambda e: None)
    assert len(n) == 1
