"""Short reminder video: one still frame (medicine + translated instruction, in the right script) + the spoken audio.

Frame is drawn with Pillow using bundled Noto fonts (Indic scripts need a font that has the glyphs, and
libraqm for correct conjuncts). The MP4 is assembled with ffmpeg (bundled via imageio-ffmpeg).
"""
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ..config import get_settings
from .languages import FONT_DIR, Language

W, H = 1280, 720
SILENT_SECONDS = 8


class VideoError(Exception):
    pass


def _ffmpeg() -> str:
    cfg = get_settings().FFMPEG_PATH
    if cfg:
        return cfg
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        found = shutil.which("ffmpeg")
        if found:
            return found
    raise VideoError("ffmpeg is not installed (pip install imageio-ffmpeg, or set FFMPEG_PATH)")


def _font(name: str, size: int):
    path = FONT_DIR / name
    if not path.exists():
        raise VideoError(f"Font file missing: {path.name}")
    return ImageFont.truetype(str(path), size)


def _runs(text: str) -> list[tuple[str, bool]]:
    """Split into runs of ASCII / non-ASCII characters. Indic fonts have no Latin glyphs (they would show as
    empty boxes), so ASCII runs (medicine names, 'mg', digits) are drawn with the Latin font."""
    runs: list[tuple[str, bool]] = []
    for ch in text:
        is_ascii = ord(ch) < 128
        if runs and runs[-1][1] == is_ascii:
            runs[-1] = (runs[-1][0] + ch, is_ascii)
        else:
            runs.append((ch, is_ascii))
    return runs


def _width(draw, text: str, script_font, latin_font) -> float:
    return sum(draw.textlength(run, font=latin_font if ascii_ else script_font) for run, ascii_ in _runs(text))


def _draw_mixed(draw, x: float, y: float, text: str, script_font, latin_font, fill) -> None:
    for run, ascii_ in _runs(text):
        font = latin_font if ascii_ else script_font
        draw.text((x, y), run, font=font, fill=fill)
        x += draw.textlength(run, font=font)


def _wrap(draw, text: str, script_font, latin_font, max_width: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if _width(draw, trial, script_font, latin_font) <= max_width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def render_frame(out_png: Path, language: Language, medicine_name: str, details: str, translated_text: str,
                 english_text: str) -> Path:
    img = Image.new("RGB", (W, H), "#f4f8fb")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 110], fill="#0b5fa5")
    latin = "NotoSans-Regular.ttf"
    d.text((50, 30), "Medicine Reminder", font=_font(latin, 48), fill="white")
    d.text((50, 140), medicine_name, font=_font(latin, 64), fill="#0b3556")
    d.text((50, 225), details, font=_font(latin, 34), fill="#3a5a73")

    body, latin_body = _font(language.font, 46), _font(latin, 46)
    y = 305
    for line in _wrap(d, translated_text, body, latin_body, W - 100)[:5]:
        _draw_mixed(d, 50, y, line, body, latin_body, "#111111")
        y += 70
    if language.code != "en":
        small = _font(latin, 26)
        lines = _wrap(d, english_text, small, small, W - 100)[:3]
        yy = H - 40 - 36 * len(lines)
        for line in lines:
            d.text((50, yy), line, font=small, fill="#667f93")
            yy += 36
    out_png.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_png)
    return out_png


def make_video(frame_png: Path, audio_mp3: Path | None, out_mp4: Path) -> Path:
    cmd = [_ffmpeg(), "-y", "-loop", "1", "-framerate", "5", "-i", str(frame_png)]
    if audio_mp3 is not None:
        cmd += ["-i", str(audio_mp3), "-c:a", "aac", "-shortest"]
    else:
        cmd += ["-t", str(SILENT_SECONDS)]
    cmd += ["-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out_mp4)]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=120)
    except subprocess.TimeoutExpired as exc:
        raise VideoError("Video generation timed out") from exc
    except OSError as exc:
        raise VideoError(f"Could not run ffmpeg: {exc}") from exc
    if proc.returncode != 0 or not out_mp4.exists() or out_mp4.stat().st_size == 0:
        raise VideoError("ffmpeg could not create the video: " + proc.stderr.decode(errors="ignore")[-300:])
    return out_mp4
