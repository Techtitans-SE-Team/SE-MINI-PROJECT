from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_roles
from ..models import (PROC_PENDING_VERIFICATION, PROC_REJECTED, PROC_VERIFIED, ROLE_ADMIN, ROLE_DOCTOR,
                      ROLE_PATIENT, VERIFICATION_PENDING, VERIFICATION_REJECTED, VERIFICATION_VERIFIED,
                      Patient, Prescription, User)
from ..schemas import PrescriptionCreate, PrescriptionOut, PrescriptionUpdate, VerifyRequest

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


def get_accessible_prescription(db: Session, user: User, prescription_id: int) -> Prescription:
    """Return the prescription only if this user is allowed to see it.
    Doctor: own prescriptions. Patient: own, verified prescriptions. Admin: all."""
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


def get_owned_editable(db: Session, user: User, prescription_id: int) -> Prescription:
    p = get_accessible_prescription(db, user, prescription_id)
    if user.role_name != ROLE_DOCTOR:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the prescribing doctor can modify a prescription")
    return p


@router.post("", response_model=PrescriptionOut, status_code=status.HTTP_201_CREATED)
def create_prescription(data: PrescriptionCreate, user: User = Depends(require_roles(ROLE_DOCTOR)),
                        db: Session = Depends(get_db)):
    """New prescriptions are always stored as Pending verification."""
    patient = db.get(Patient, data.patient_id)
    if patient is None or patient.status != "Active":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Patient not found")
    p = Prescription(**data.model_dump(), doctor_id=user.doctor.doctor_id,
                     verification_status=VERIFICATION_PENDING, processing_status=PROC_PENDING_VERIFICATION,
                     status="Active")
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
    p = get_owned_editable(db, user, prescription_id)
    changes = data.model_dump(exclude_unset=True)
    content_changed = any(k != "status" for k in changes)
    if p.verification_status == VERIFICATION_VERIFIED and content_changed:
        raise HTTPException(status.HTTP_409_CONFLICT, "A verified prescription cannot be edited")
    for field, value in changes.items():
        if value is None and field != "instructions":
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"{field} cannot be empty")
        setattr(p, field, " ".join(value.split()) if isinstance(value, str) and field != "instructions" else value)
    db.commit()
    db.refresh(p)
    return p


@router.post("/{prescription_id}/verify", response_model=PrescriptionOut)
def verify_prescription(prescription_id: int, data: VerifyRequest | None = None,
                        user: User = Depends(require_roles(ROLE_DOCTOR)), db: Session = Depends(get_db)):
    p = get_owned_editable(db, user, prescription_id)
    action = data.action if data else "verify"
    if action == "verify":
        p.verification_status, p.processing_status = VERIFICATION_VERIFIED, PROC_VERIFIED
    else:
        p.verification_status, p.processing_status = VERIFICATION_REJECTED, PROC_REJECTED
    db.commit()
    db.refresh(p)
    return p
