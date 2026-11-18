"""Translation -> audio -> video pipeline and its integration with the verification workflow."""
import subprocess

import pytest
from deep_translator.exceptions import TooManyRequests
from gtts import gTTSError

from app.config import get_settings
from app.services import translation, tts, video
from app.services.languages import resolve_language
from tests.conftest import patient_id, rx_payload


def _fake_mp3(text, code, path):
    """A real (silent) audio file so ffmpeg can build a real video."""
    subprocess.run([video._ffmpeg(), "-y", "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono", "-t", "1",
                    "-q:a", "9", str(path)], capture_output=True, check=True)


@pytest.fixture(autouse=True)
def mocked_google(monkeypatch):
    translation._cache.clear()
    translation.guard.reset()
    tts.guard.reset()
    monkeypatch.setattr(translation, "_google",
                        lambda text, code: f"[{code}] Paracetamol 500 mg ತೆಗೆದುಕೊಳ್ಳಿ")
    monkeypatch.setattr(tts, "_synthesize", _fake_mp3)


@pytest.fixture()
def verified(client, doctor, patient):
    pid = patient_id(client, doctor["headers"])
    rx = client.post("/prescriptions", json=rx_payload(pid), headers=doctor["headers"]).json()
    return rx["prescription_id"], rx["medicines"] and rx["medicines"][0]["medicine_id"], pid


def _verify(client, doctor, rx_id):
    r = client.post(f"/prescriptions/{rx_id}/verify", json={"action": "verify"}, headers=doctor["headers"])
    assert r.status_code == 200, r.text


def test_cannot_generate_for_unverified(client, doctor, verified):
    r = client.post(f"/prescriptions/{verified[0]}/media", headers=doctor["headers"])
    assert r.status_code == 409


def test_full_pipeline_produces_text_audio_and_video(client, doctor, patient, verified):
    _verify(client, doctor, verified[0])
    r = client.post(f"/prescriptions/{verified[0]}/media", headers=doctor["headers"])   # patient language = Kannada
    assert r.status_code == 200, r.text
    item = r.json()[0]
    assert item["status"] == "Completed" and item["language_code"] == "kn"
    assert item["has_audio"] and item["has_video"] and item["translated"]
    assert "Paracetamol" in item["translated_text"]

    mp4 = client.get(f"/media/{item['media_id']}/video", headers=patient["headers"])   # patient can watch
    assert mp4.status_code == 200 and mp4.headers["content-type"] == "video/mp4"
    assert mp4.content[4:8] == b"ftyp"                                                   # genuine MP4
    assert client.get(f"/media/{item['media_id']}/audio", headers=patient["headers"]).status_code == 200


def test_translation_rate_limit_does_not_break_pipeline(client, doctor, verified, monkeypatch):
    def limited(text, code):
        raise TooManyRequests()
    monkeypatch.setattr(translation, "_google", limited)
    _verify(client, doctor, verified[0])
    r = client.post(f"/prescriptions/{verified[0]}/media", headers=doctor["headers"])
    assert r.status_code == 200
    item = r.json()[0]
    assert item["status"] == "Partial" and not item["translated"]
    assert "rate limited" in item["message"] and "Take Paracetamol" in item["translated_text"]


def test_tts_failure_still_gives_text_and_silent_video(client, doctor, verified, monkeypatch):
    def limited(text, code, path):
        raise gTTSError("429 Too Many Requests")
    monkeypatch.setattr(tts, "_synthesize", limited)
    _verify(client, doctor, verified[0])
    item = client.post(f"/prescriptions/{verified[0]}/media", headers=doctor["headers"]).json()[0]
    assert item["status"] == "Partial" and not item["has_audio"] and item["has_video"]
    assert "No audio" in item["message"]


def test_partial_result_is_retried_but_completed_is_reused(client, doctor, verified, monkeypatch):
    calls = []
    monkeypatch.setattr(translation, "_google", lambda t, c: calls.append(1) or "[kn] Paracetamol 500")
    _verify(client, doctor, verified[0])
    client.post(f"/prescriptions/{verified[0]}/media", headers=doctor["headers"])
    client.post(f"/prescriptions/{verified[0]}/media", headers=doctor["headers"])
    assert len(calls) == 1                      # second call reused the finished item
    client.post(f"/prescriptions/{verified[0]}/media?regenerate=true", headers=doctor["headers"])
    assert len(client.get(f"/prescriptions/{verified[0]}/media", headers=doctor["headers"]).json()) == 1


def test_other_language_and_unsupported_language(client, doctor, verified):
    _verify(client, doctor, verified[0])
    hi = client.post(f"/prescriptions/{verified[0]}/media?language=Hindi", headers=doctor["headers"]).json()
    assert hi[0]["language_code"] == "hi"
    bad = client.post(f"/prescriptions/{verified[0]}/media?language=Klingon", headers=doctor["headers"])
    assert bad.status_code == 422 and "Supported" in bad.json()["detail"]


def test_access_control(client, doctor, doctor2, patient, patient2, verified):
    _verify(client, doctor, verified[0])
    item = client.post(f"/prescriptions/{verified[0]}/media", headers=doctor["headers"]).json()[0]
    for other in (doctor2, patient2):
        assert client.get(f"/media/{item['media_id']}/video", headers=other["headers"]).status_code == 403
        assert client.get(f"/prescriptions/{verified[0]}/media", headers=other["headers"]).status_code == 403
    assert client.get(f"/media/{item['media_id']}/video").status_code == 401
    assert client.get("/media/9999/video", headers=doctor["headers"]).status_code == 404


def test_verification_triggers_media_generation_for_patient_language(client, doctor, patient, verified):
    get_settings().AUTO_GENERATE_MEDIA = True
    try:
        _verify(client, doctor, verified[0])
    finally:
        get_settings().AUTO_GENERATE_MEDIA = False
    items = client.get(f"/prescriptions/{verified[0]}/media", headers=patient["headers"]).json()
    assert len(items) == 1 and items[0]["language_code"] == "kn" and items[0]["status"] == "Completed"


def test_rejected_prescription_generates_nothing(client, doctor, verified):
    get_settings().AUTO_GENERATE_MEDIA = True
    try:
        client.post(f"/prescriptions/{verified[0]}/verify", json={"action": "reject"}, headers=doctor["headers"])
    finally:
        get_settings().AUTO_GENERATE_MEDIA = False
    assert client.get(f"/prescriptions/{verified[0]}/media", headers=doctor["headers"]).json() == []


def test_languages_endpoint(client):
    names = [x["name"] for x in client.get("/languages").json()]
    assert {"English", "Hindi", "Kannada", "Tamil", "Telugu", "Malayalam"} <= set(names)


@pytest.mark.parametrize("code", ["hi", "kn", "ta", "te", "ml", "bn", "gu", "pa", "mr"])
def test_frame_renders_in_every_script(tmp_path, code):
    from PIL import Image
    samples = {"hi": "दवा लें", "mr": "औषध घ्या", "kn": "ಔಷಧಿ ತೆಗೆದುಕೊಳ್ಳಿ", "ta": "மருந்து சாப்பிடுங்கள்",
               "te": "మందు వేసుకోండి", "ml": "മരുന്ന് കഴിക്കുക", "bn": "ওষুধ খান", "gu": "દવા લો", "pa": "ਦਵਾਈ ਲਓ"}
    png = video.render_frame(tmp_path / "f.png", resolve_language(code), "Paracetamol", "500 mg | BD | 5 days",
                             samples[code], "Take Paracetamol")
    img = Image.open(png)
    assert img.size == (1280, 720) and len(set(img.convert("L").resize((64, 36)).getdata())) > 3


def test_latin_text_inside_indic_line_uses_latin_font():
    runs = video._runs("ಪ್ಯಾರಸಿಟಮಾಲ್ 500 mg ಅನ್ನು")
    assert [(t.strip(), a) for t, a in runs if t.strip()] == [("ಪ್ಯಾರಸಿಟಮಾಲ್", False), ("500 mg", True), ("ಅನ್ನು", False)]
