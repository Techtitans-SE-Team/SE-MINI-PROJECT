from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_roles
from ..models import ROLE_ADMIN, ROLE_DOCTOR, ROLE_PATIENT, Patient, Prescription, User
from ..schemas import PatientBrief, PatientOut, PatientUpdate

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("/me", response_model=PatientOut)
def my_profile(user: User = Depends(require_roles(ROLE_PATIENT))):
    return user.patient


@router.put("/me", response_model=PatientOut)
def update_my_profile(data: PatientUpdate, user: User = Depends(require_roles(ROLE_PATIENT)),
                      db: Session = Depends(get_db)):
    patient = user.patient
    changes = data.model_dump(exclude_unset=True)
    if "name" in changes:
        user.name = " ".join(changes.pop("name").split())
    for field in ("date_of_birth", "phone", "preferred_language"):
        if field in changes and changes[field] is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"{field} cannot be empty")
    for field, value in changes.items():
        setattr(patient, field, value)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("", response_model=list[PatientBrief])
def list_patients(search: str | None = Query(default=None, max_length=100),
                  user: User = Depends(require_roles(ROLE_DOCTOR, ROLE_ADMIN)),
                  db: Session = Depends(get_db)):
    """Minimal patient list so doctors can pick a patient to prescribe for."""
    stmt = select(Patient).join(User, Patient.user_id == User.user_id).where(Patient.status == "Active")
    if search:
        stmt = stmt.where(User.name.ilike(f"%{search}%"))
    return db.scalars(stmt.order_by(User.name)).all()


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Patient not found")
    if user.role_name == ROLE_ADMIN:
        return patient
    if user.role_name == ROLE_PATIENT and patient.user_id == user.user_id:
        return patient
    if user.role_name == ROLE_DOCTOR and db.scalar(
            select(Prescription.prescription_id).where(
                Prescription.patient_id == patient_id,
                Prescription.doctor_id == user.doctor.doctor_id).limit(1)):
        return patient
    raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have access to this patient's record")
