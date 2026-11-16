import uuid
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..deps import get_current_user, require_roles
from ..models import (CONFIRMED, EXTRACTED, FILE_FAILED, FILE_PROCESSED, FILE_PROCESSING, NEEDS_REVIEW,
                      PROC_PENDING_VERIFICATION, PROC_PROCESSING, PROC_REJECTED, PROC_UPLOADED, PROC_VERIFIED,
                      ROLE_ADMIN, ROLE_DOCTOR, ROLE_PATIENT, VERIFICATION_PENDING, VERIFICATION_REJECTED,
                      VERIFICATION_VERIFIED, Medicine, Patient, Prescription, PrescriptionFile, User)
from ..schemas import (MedicineCreate, MedicineOut, MedicineUpdate, PrescriptionCreate, PrescriptionOut,
                       PrescriptionUpdate, UploadResponse, VerifyRequest)
from ..services import ocr
from ..services.extraction import NOT_DETECTED, extract_medicines

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])

ALLOWED_TYPES = {  # extension -> (file_type, magic-byte check)
    "jpg": ("jpg", lambda b: b.startswith(b"\xff\xd8\xff")),
    "jpeg": ("jpg", lambda b: b.startswith(b"\xff\xd8\xff")),
    "png": ("png", lambda b: b.startswith(b"\x89PNG\r\n\x1a\n")),
    "pdf": ("pdf", lambda b: b.startswith(b"%PDF")),
}


# ------------------------------------------------------------------ access helpers
def get_accessible_prescription(db: Session, user: User, prescription_id: int) -> Prescription:
    """Doctor: own prescriptions. Patient: own, verified prescriptions. Admin: all."""
    p = db.get(Prescription, prescription_id)
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Prescription not found")
    role = user.role_name
    if role == ROLE_ADMIN:
        return p
    if role == ROLE_DOCTOR and p.doctor_id == user.doctor.doctor_id:
        return p
    if (role == ROLE_PATIENT and p.patient_id == user.patient.patient_id
            and p.verification_status == VERIFICATION_VERIFIED):
        return p
    raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have access to this prescription")


def get_owned(db: Session, user: User, prescription_id: int) -> Prescription:
    p = get_accessible_prescription(db, user, prescription_id)
    if user.role_name != ROLE_DOCTOR:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the prescribing doctor can modify a prescription")
    return p


def ensure_not_verified(p: Prescription):
    if p.verification_status == VERIFICATION_VERIFIED:
        raise HTTPException(status.HTTP_409_CONFLICT, "A verified prescription cannot be edited")


def sync_header(p: Prescription):
    """The prescription row mirrors its first medicine (keeps the Sprint 1 fields consistent)."""
    if p.medicines:
        m = p.medicines[0]
        p.medicine_name, p.dosage, p.frequency, p.duration, p.instructions = (
            m.medicine_name, m.dosage, m.frequency, m.duration, m.instructions)


def _clean(v):
    return " ".join(v.split()) if isinstance(v, str) else v


def _review_status(m: Medicine) -> str:
    return NEEDS_REVIEW if NOT_DETECTED in (m.medicine_name, m.dosage, m.frequency, m.duration) else CONFIRMED


# ------------------------------------------------------------------ Sprint 1: CRUD
@router.post("", response_model=PrescriptionOut, status_code=status.HTTP_201_CREATED)
def create_prescription(data: PrescriptionCreate, user: User = Depends(require_roles(ROLE_DOCTOR)),
                        db: Session = Depends(get_db)):
    """Manually entered prescriptions are always stored as Pending verification."""
    patient = db.get(Patient, data.patient_id)
    if patient is None or patient.status != "Active":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Patient not found")
    fields = data.model_dump()
    p = Prescription(**fields, doctor_id=user.doctor.doctor_id, verification_status=VERIFICATION_PENDING,
                     processing_status=PROC_PENDING_VERIFICATION, status="Active")
    p.medicines.append(Medicine(**{k: fields[k] for k in
                                   ("medicine_name", "dosage", "frequency", "duration", "instructions")},
                                extraction_status=CONFIRMED))  # doctor-entered, so already confirmed
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.get("", response_model=list[PrescriptionOut])
def list_prescriptions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(Prescription).order_by(Prescription.prescription_id.desc())
    if user.role_name == ROLE_DOCTOR:
        stmt = stmt.where(Prescription.doctor_id == user.doctor.doctor_id)
    elif user.role_name == ROLE_PATIENT:
        stmt = stmt.where(Prescription.patient_id == user.patient.patient_id,
                          Prescription.verification_status == VERIFICATION_VERIFIED)
    return db.scalars(stmt).all()


@router.get("/{prescription_id}", response_model=PrescriptionOut)
def get_prescription(prescription_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_accessible_prescription(db, user, prescription_id)


@router.put("/{prescription_id}", response_model=PrescriptionOut)
def update_prescription(prescription_id: int, data: PrescriptionUpdate,
                        user: User = Depends(require_roles(ROLE_DOCTOR)), db: Session = Depends(get_db)):
    p = get_owned(db, user, prescription_id)
    changes = data.model_dump(exclude_unset=True)
    content = {k: v for k, v in changes.items() if k != "status"}
    if content:
        ensure_not_verified(p)
    for field, value in changes.items():
        if value is None and field != "instructions":
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"{field} cannot be empty")
        setattr(p, field, value if field == "instructions" else _clean(value))
    if content and p.medicines:  # keep first medicine row in step with the header
        m = p.medicines[0]
        for field in content:
            setattr(m, field, getattr(p, field))
        m.extraction_status = _review_status(m)
    db.commit()
    db.refresh(p)
    return p


@router.post("/{prescription_id}/verify", response_model=PrescriptionOut)
def verify_prescription(prescription_id: int, data: VerifyRequest | None = None,
                        user: User = Depends(require_roles(ROLE_DOCTOR)), db: Session = Depends(get_db)):
    p = get_owned(db, user, prescription_id)
    action = data.action if data else "verify"
    if action == "verify":
        if any(m.extraction_status == NEEDS_REVIEW for m in p.medicines):
            raise HTTPException(status.HTTP_409_CONFLICT,
                                "Some medicines have missing or unconfirmed details. Review and correct them first")
        if p.files and not p.medicines:
            raise HTTPException(status.HTTP_409_CONFLICT,
                                "No medicines were extracted. Add the medicine details before verifying")
        for m in p.medicines:
            m.extraction_status = CONFIRMED
        p.verification_status, p.processing_status = VERIFICATION_VERIFIED, PROC_VERIFIED
    else:
        p.verification_status, p.processing_status = VERIFICATION_REJECTED, PROC_REJECTED
    db.commit()
    db.refresh(p)
    return p


# ------------------------------------------------------------------ Sprint 2: upload + OCR
def _validate_upload(file: UploadFile, max_bytes: int) -> tuple[bytes, str]:
    name = file.filename or ""
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext not in ALLOWED_TYPES:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Only JPG, PNG or PDF files are allowed")
    content = file.file.read(max_bytes + 1)
    if not content:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The uploaded file is empty")
    if len(content) > max_bytes:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            f"File is too large (maximum {max_bytes // (1024 * 1024)} MB)")
    file_type, magic_ok = ALLOWED_TYPES[ext]
    if not magic_ok(content):
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "File content does not match its extension")
    return content, file_type


def _process_file(db: Session, p: Prescription, f: PrescriptionFile) -> tuple[str, str]:
    """Run OCR + extraction, replace existing medicines. Returns (ocr_status, message)."""
    p.processing_status, f.upload_status = PROC_PROCESSING, FILE_PROCESSING
    db.commit()
    try:
        text = ocr.extract_text(f.stored_file_path, f.file_type)
    except ocr.OCRUnavailable as exc:
        f.upload_status, p.processing_status = FILE_FAILED, PROC_UPLOADED
        db.commit()
        return "failed", f"Text could not be read from the file ({exc}). Enter the medicines manually"

    for m in list(p.medicines):
        p.medicines.remove(m)
    found = extract_medicines(text)
    for e in found:
        p.medicines.append(Medicine(
            medicine_name=e.medicine_name[:150], dosage=e.dosage[:100], frequency=e.frequency[:100],
            duration=e.duration[:100], instructions=e.instructions,
            extraction_status=NEEDS_REVIEW if e.needs_review else EXTRACTED))
    sync_header(p)
    f.upload_status, p.processing_status = FILE_PROCESSED, PROC_PENDING_VERIFICATION
    db.commit()
    if not found:
        return "no_medicines_found", "No medicines were detected. Please enter them manually"
    review = sum(m.extraction_status == NEEDS_REVIEW for m in p.medicines)
    msg = f"{len(found)} medicine(s) extracted"
    return "success", msg + (f"; {review} need review because some details are missing" if review else "")


def _upload_response(p: Prescription, ocr_status: str, message: str) -> UploadResponse:
    base = PrescriptionOut.model_validate(p).model_dump()
    return UploadResponse(**base, ocr_status=ocr_status, message=message)


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
def upload_prescription(patient_id: int = Form(...), prescription_date: date | None = Form(None),
                        file: UploadFile = File(...), user: User = Depends(require_roles(ROLE_DOCTOR)),
                        db: Session = Depends(get_db)):
    """Upload a prescription image/PDF, run OCR and store the extracted medicines for doctor review."""
    settings = get_settings()
    patient = db.get(Patient, patient_id)
    if patient is None or patient.status != "Active":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Patient not found")
    rx_date = prescription_date or date.today()
    if rx_date > date.today():
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "prescription_date cannot be in the future")
    content, file_type = _validate_upload(file, settings.MAX_UPLOAD_MB * 1024 * 1024)

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored = upload_dir / f"{uuid.uuid4().hex}.{file_type}"   # never use the client's file name on disk
    stored.write_bytes(content)

    p = Prescription(patient_id=patient_id, doctor_id=user.doctor.doctor_id, prescription_date=rx_date,
                     medicine_name="Pending extraction", dosage=NOT_DETECTED, frequency=NOT_DETECTED,
                     duration=NOT_DETECTED, verification_status=VERIFICATION_PENDING,
                     processing_status=PROC_UPLOADED, status="Active")
    f = PrescriptionFile(original_file_name=Path(file.filename).name[:255], stored_file_path=str(stored),
                         file_type=file_type, file_size=len(content))
    p.files.append(f)
    db.add(p)
    db.commit()

    ocr_status, message = _process_file(db, p, f)
    db.refresh(p)
    return _upload_response(p, ocr_status, message)


@router.post("/{prescription_id}/reprocess", response_model=UploadResponse)
def reprocess_prescription(prescription_id: int, user: User = Depends(require_roles(ROLE_DOCTOR)),
                           db: Session = Depends(get_db)):
    p = get_owned(db, user, prescription_id)
    ensure_not_verified(p)
    if not p.files:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "This prescription has no uploaded file")
    ocr_status, message = _process_file(db, p, p.files[-1])
    db.refresh(p)
    return _upload_response(p, ocr_status, message)


@router.get("/{prescription_id}/file")
def download_file(prescription_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    p = get_accessible_prescription(db, user, prescription_id)
    if not p.files or not Path(p.files[-1].stored_file_path).exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No file stored for this prescription")
    f = p.files[-1]
    return FileResponse(f.stored_file_path, filename=f.original_file_name)


# ------------------------------------------------------------------ Sprint 2: extracted medicines
@router.get("/{prescription_id}/medicines", response_model=list[MedicineOut])
def list_medicines(prescription_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_accessible_prescription(db, user, prescription_id).medicines


@router.post("/{prescription_id}/medicines", response_model=MedicineOut, status_code=status.HTTP_201_CREATED)
def add_medicine(prescription_id: int, data: MedicineCreate, user: User = Depends(require_roles(ROLE_DOCTOR)),
                 db: Session = Depends(get_db)):
    p = get_owned(db, user, prescription_id)
    ensure_not_verified(p)
    m = Medicine(**data.model_dump(), extraction_status=CONFIRMED)
    p.medicines.append(m)
    sync_header(p)
    db.commit()
    db.refresh(m)
    return m


def _get_medicine(p: Prescription, medicine_id: int) -> Medicine:
    m = next((m for m in p.medicines if m.medicine_id == medicine_id), None)
    if m is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Medicine not found on this prescription")
    return m


@router.put("/{prescription_id}/medicines/{medicine_id}", response_model=MedicineOut)
def update_medicine(prescription_id: int, medicine_id: int, data: MedicineUpdate,
                    user: User = Depends(require_roles(ROLE_DOCTOR)), db: Session = Depends(get_db)):
    """Doctor corrects extracted details. Once no field is missing the medicine becomes Confirmed."""
    p = get_owned(db, user, prescription_id)
    ensure_not_verified(p)
    m = _get_medicine(p, medicine_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is None and field != "instructions":
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"{field} cannot be empty")
        setattr(m, field, value if field == "instructions" else _clean(value))
    m.extraction_status = _review_status(m)
    sync_header(p)
    db.commit()
    db.refresh(m)
    return m


@router.delete("/{prescription_id}/medicines/{medicine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medicine(prescription_id: int, medicine_id: int, user: User = Depends(require_roles(ROLE_DOCTOR)),
                    db: Session = Depends(get_db)):
    p = get_owned(db, user, prescription_id)
    ensure_not_verified(p)
    p.medicines.remove(_get_medicine(p, medicine_id))
    sync_header(p)
    db.commit()
