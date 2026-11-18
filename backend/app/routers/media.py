from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import (ROLE_ADMIN, ROLE_DOCTOR, ROLE_PATIENT, VERIFICATION_VERIFIED, InstructionMedia, User)
from ..schemas import MediaOut
from ..services import media_pipeline
from ..services.languages import LANGUAGES, resolve_language, supported_names
from .prescriptions import get_accessible_prescription

router = APIRouter(tags=["Multilingual Media"])


@router.get("/languages")
def list_languages():
    """Languages available for translation, audio and video."""
    return [{"name": lang.name, "code": lang.code} for lang in LANGUAGES]


@router.post("/prescriptions/{prescription_id}/media", response_model=list[MediaOut])
def generate_media(prescription_id: int, language: str | None = Query(default=None, description="Language name or code"),
                   regenerate: bool = False, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Translate the instructions and generate audio + video for every medicine of a VERIFIED prescription.
    Language defaults to the patient's preferred language. Safe to call again: finished items are reused."""
    rx = get_accessible_prescription(db, user, prescription_id)
    if rx.verification_status != VERIFICATION_VERIFIED:
        raise HTTPException(status.HTTP_409_CONFLICT, "The prescription must be verified before reminders are generated")
    lang = resolve_language(language or rx.patient.preferred_language)
    if lang is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            f"Unsupported language. Supported: {', '.join(supported_names())}")
    if not rx.medicines:
        raise HTTPException(status.HTTP_409_CONFLICT, "This prescription has no medicines")
    return media_pipeline.generate_for_prescription(db, rx, lang, regenerate)


@router.get("/prescriptions/{prescription_id}/media", response_model=list[MediaOut])
def list_media(prescription_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_accessible_prescription(db, user, prescription_id)
    return db.scalars(select(InstructionMedia).where(InstructionMedia.prescription_id == prescription_id)
                      .order_by(InstructionMedia.media_id)).all()


def _media_for(db: Session, user: User, media_id: int) -> InstructionMedia:
    media = db.get(InstructionMedia, media_id)
    if media is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Media not found")
    get_accessible_prescription(db, user, media.prescription_id)  # same access rules as the prescription
    return media


def _file(path: str | None, media_type: str, what: str):
    if not path or not Path(path).exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No {what} available for this item")
    return FileResponse(path, media_type=media_type)


@router.get("/media/{media_id}/audio")
def get_audio(media_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _file(_media_for(db, user, media_id).audio_path, "audio/mpeg", "audio")


@router.get("/media/{media_id}/video")
def get_video(media_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _file(_media_for(db, user, media_id).video_path, "video/mp4", "video")
