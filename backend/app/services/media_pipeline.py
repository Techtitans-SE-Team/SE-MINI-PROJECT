"""Verified prescription -> translated instruction -> audio -> video, one InstructionMedia row per medicine+language.

Every stage is isolated: a failure (rate limit, offline, missing codec) is recorded on the row and never raises,
so the prescription workflow is never blocked and the patient still gets whatever stage did succeed.
"""
import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import InstructionMedia, Medicine, Prescription, VERIFICATION_VERIFIED
from . import translation, tts, video
from .languages import Language

log = logging.getLogger(__name__)


def media_root() -> Path:
    return Path(get_settings().MEDIA_DIR)


def generate_for_medicine(db: Session, rx: Prescription, med: Medicine, lang: Language,
                          regenerate: bool = False) -> InstructionMedia:
    row = db.scalar(select(InstructionMedia).where(InstructionMedia.medicine_id == med.medicine_id,
                                                   InstructionMedia.language_code == lang.code))
    if row and row.status == "Completed" and not regenerate:
        return row

    english = translation.build_instruction_text(med.medicine_name, med.dosage, med.frequency, med.duration,
                                                 med.instructions)
    notes: list[str] = []

    tr = translation.translate_instruction(english, lang, medicine_name=med.medicine_name, dosage=med.dosage)
    if tr.warning:
        notes.append(tr.warning)

    folder = media_root() / str(rx.prescription_id)
    stem = f"{med.medicine_id}_{lang.code}"
    audio_path = video_path = None

    # Audio is spoken in the language that was actually produced (English if translation fell back)
    try:
        audio_path = str(tts.synthesize(tr.text, tr.language, folder / f"{stem}.mp3"))
    except tts.TTSError as exc:
        notes.append(f"No audio: {exc}")

    try:
        frame = video.render_frame(
            folder / f"{stem}.png", lang if tr.translated else _english(), med.medicine_name,
            f"{med.dosage}  |  {med.frequency}  |  {med.duration}", tr.text, english)
        video_path = str(video.make_video(frame, Path(audio_path) if audio_path else None, folder / f"{stem}.mp4"))
        frame.unlink(missing_ok=True)
    except video.VideoError as exc:
        notes.append(f"No video: {exc}")
    except Exception as exc:  # noqa: BLE001 - never let media break the workflow
        log.exception("video generation failed")
        notes.append(f"No video: {exc.__class__.__name__}")

    status = ("Completed" if tr.translated and audio_path and video_path
              else "Failed" if not audio_path and not video_path else "Partial")
    if row is None:
        row = InstructionMedia(prescription_id=rx.prescription_id, medicine_id=med.medicine_id,
                               language_code=lang.code, language_name=lang.name, source_text=english,
                               translated_text=tr.text)
        db.add(row)
    row.source_text, row.translated_text, row.translated = english, tr.text, tr.translated
    row.audio_path, row.video_path, row.status = audio_path, video_path, status
    row.message = "; ".join(notes) or None
    db.commit()
    db.refresh(row)
    return row


def _english() -> Language:
    from .languages import resolve_language
    return resolve_language("en")


def generate_for_prescription(db: Session, rx: Prescription, lang: Language, regenerate: bool = False) -> list[InstructionMedia]:
    if rx.verification_status != VERIFICATION_VERIFIED:
        raise ValueError("Only verified prescriptions can be converted to reminders")
    return [generate_for_medicine(db, rx, m, lang, regenerate) for m in rx.medicines]


def auto_generate(bind, prescription_id: int) -> None:
    """Background task run after verification (own DB session; swallows every error)."""
    from sqlalchemy.orm import Session as _S
    from .languages import resolve_language
    try:
        with _S(bind=bind, expire_on_commit=False) as db:
            rx = db.get(Prescription, prescription_id)
            if rx is None or rx.verification_status != VERIFICATION_VERIFIED:
                return
            lang = resolve_language(rx.patient.preferred_language)
            if lang is None:
                log.info("Preferred language %r not supported; skipping media", rx.patient.preferred_language)
                return
            generate_for_prescription(db, rx, lang)
    except Exception:  # noqa: BLE001
        log.exception("Automatic media generation failed for prescription %s", prescription_id)
