from datetime import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_roles
from ..models import (ROLE_PATIENT, VERIFICATION_VERIFIED, Medicine, MedicineReminder, Prescription, User)
from ..schemas import MedicineReminderCreate, MedicineReminderUpdate
from ..services.scheduler import now_local, suggest_times

router = APIRouter(prefix="/reminders", tags=["Medicine Reminders"])


def get_patient_id(user: User) -> int:
    if not user.patient:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Patient profile not found")
    return user.patient.patient_id


def reminder_details(reminder: MedicineReminder, medicine: Medicine) -> dict:
    return {
        "reminder_id": reminder.reminder_id, "medicine_id": reminder.medicine_id,
        "patient_id": reminder.patient_id, "prescription_id": medicine.prescription_id,
        "medicine_name": medicine.medicine_name, "dosage": medicine.dosage, "frequency": medicine.frequency,
        "reminder_time": reminder.reminder_time, "is_active": reminder.is_active, "created_at": reminder.created_at,
    }


def _own_active_medicine(db: Session, patient_id: int, medicine_id: int) -> Medicine | None:
    return db.scalar(
        select(Medicine).join(Prescription, Medicine.prescription_id == Prescription.prescription_id)
        .where(Medicine.medicine_id == medicine_id, Prescription.patient_id == patient_id,
               Prescription.verification_status == VERIFICATION_VERIFIED, Prescription.status == "Active"))


def _duplicate(db: Session, medicine_id: int, at: time, exclude_id: int | None = None) -> bool:
    stmt = select(MedicineReminder.reminder_id).where(MedicineReminder.medicine_id == medicine_id,
                                                      MedicineReminder.reminder_time == at)
    if exclude_id:
        stmt = stmt.where(MedicineReminder.reminder_id != exclude_id)
    return db.scalar(stmt) is not None


@router.post("", status_code=status.HTTP_201_CREATED)
def create_reminder(data: MedicineReminderCreate, user: User = Depends(require_roles(ROLE_PATIENT)),
                    db: Session = Depends(get_db)):
    patient_id = get_patient_id(user)
    medicine = _own_active_medicine(db, patient_id, data.medicine_id)
    if medicine is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Medicine not found in your active verified prescriptions")
    if _duplicate(db, medicine.medicine_id, data.reminder_time):
        raise HTTPException(status.HTTP_409_CONFLICT, "A reminder for this medicine at this time already exists")
    reminder = MedicineReminder(medicine_id=medicine.medicine_id, patient_id=patient_id,
                                reminder_time=data.reminder_time, is_active=True)
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder_details(reminder, medicine)


@router.post("/auto/{prescription_id}", status_code=status.HTTP_201_CREATED)
def create_reminders_from_prescription(prescription_id: int, user: User = Depends(require_roles(ROLE_PATIENT)),
                                       db: Session = Depends(get_db)):
    """Schedule reminders for every medicine in a verified prescription, using its frequency (e.g. 1-0-1, BD)."""
    patient_id = get_patient_id(user)
    rx = db.get(Prescription, prescription_id)
    if (rx is None or rx.patient_id != patient_id or rx.verification_status != VERIFICATION_VERIFIED
            or rx.status != "Active"):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Active verified prescription not found")
    out, unscheduled = [], []
    for med in rx.medicines:
        times = suggest_times(med.frequency)
        if not times:
            unscheduled.append(med.medicine_name)
        for t in times:
            if not _duplicate(db, med.medicine_id, t):
                r = MedicineReminder(medicine_id=med.medicine_id, patient_id=patient_id, reminder_time=t, is_active=True)
                db.add(r)
                db.flush()
                out.append(reminder_details(r, med))
    db.commit()
    return {"created": out, "needs_manual_time": unscheduled}


@router.get("")
def list_reminders(user: User = Depends(require_roles(ROLE_PATIENT)), db: Session = Depends(get_db)):
    patient_id = get_patient_id(user)
    rows = db.execute(select(MedicineReminder, Medicine).join(Medicine, Medicine.medicine_id == MedicineReminder.medicine_id)
                      .where(MedicineReminder.patient_id == patient_id).order_by(MedicineReminder.reminder_time)).all()
    return [reminder_details(r, m) for r, m in rows]


@router.get("/due")
def due_reminders(user: User = Depends(require_roles(ROLE_PATIENT)), db: Session = Depends(get_db)):
    """Active reminders whose time has already passed today (frontend can use this to show 'take now')."""
    patient_id = get_patient_id(user)
    now = now_local().time()
    rows = db.execute(select(MedicineReminder, Medicine).join(Medicine, Medicine.medicine_id == MedicineReminder.medicine_id)
                      .where(MedicineReminder.patient_id == patient_id, MedicineReminder.is_active.is_(True),
                             MedicineReminder.reminder_time <= now).order_by(MedicineReminder.reminder_time)).all()
    return [reminder_details(r, m) for r, m in rows]


def _own_reminder(db: Session, user: User, reminder_id: int) -> MedicineReminder:
    reminder = db.scalar(select(MedicineReminder).where(MedicineReminder.reminder_id == reminder_id,
                                                        MedicineReminder.patient_id == get_patient_id(user)))
    if reminder is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reminder not found")
    return reminder


@router.patch("/{reminder_id}")
def update_reminder(reminder_id: int, data: MedicineReminderUpdate, user: User = Depends(require_roles(ROLE_PATIENT)),
                    db: Session = Depends(get_db)):
    reminder = _own_reminder(db, user, reminder_id)
    changes = data.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Provide reminder_time or is_active")
    for field, value in changes.items():
        if value is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"{field} cannot be empty")
    if "reminder_time" in changes and _duplicate(db, reminder.medicine_id, changes["reminder_time"], reminder.reminder_id):
        raise HTTPException(status.HTTP_409_CONFLICT, "A reminder for this medicine at this time already exists")
    for field, value in changes.items():
        setattr(reminder, field, value)
    db.commit()
    db.refresh(reminder)
    return reminder_details(reminder, db.get(Medicine, reminder.medicine_id))


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(reminder_id: int, user: User = Depends(require_roles(ROLE_PATIENT)), db: Session = Depends(get_db)):
    db.delete(_own_reminder(db, user, reminder_id))
    db.commit()
