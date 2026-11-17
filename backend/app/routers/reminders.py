
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_roles
from ..models import (
    ROLE_PATIENT,
    VERIFICATION_VERIFIED,
    Medicine,
    MedicineReminder,
    Prescription,
    User,
)
from ..schemas import MedicineReminderCreate, MedicineReminderUpdate

router = APIRouter(prefix="/reminders", tags=["Medicine Reminders"])


def get_patient_id(user: User) -> int:
    if not user.patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found",
        )
    return user.patient.patient_id


def reminder_details(reminder: MedicineReminder, medicine: Medicine) -> dict:
    return {
        "reminder_id": reminder.reminder_id,
        "medicine_id": reminder.medicine_id,
        "patient_id": reminder.patient_id,
        "medicine_name": medicine.medicine_name,
        "dosage": medicine.dosage,
        "reminder_time": reminder.reminder_time,
        "is_active": reminder.is_active,
        "created_at": reminder.created_at,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_reminder(
    data: MedicineReminderCreate,
    user: User = Depends(require_roles(ROLE_PATIENT)),
    db: Session = Depends(get_db),
):
    patient_id = get_patient_id(user)

    medicine = db.scalar(
        select(Medicine)
        .join(Prescription, Medicine.prescription_id == Prescription.prescription_id)
        .where(
            Medicine.medicine_id == data.medicine_id,
            Prescription.patient_id == patient_id,
            Prescription.verification_status == VERIFICATION_VERIFIED,
            Prescription.status == "Active",
        )
    )

    if medicine is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found in your active verified prescriptions",
        )

    reminder = MedicineReminder(
        medicine_id=medicine.medicine_id,
        patient_id=patient_id,
        reminder_time=data.reminder_time,
        is_active=True,
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return reminder_details(reminder, medicine)


@router.get("")
def list_reminders(
    user: User = Depends(require_roles(ROLE_PATIENT)),
    db: Session = Depends(get_db),
):
    patient_id = get_patient_id(user)

    rows = db.execute(
        select(MedicineReminder, Medicine)
        .join(Medicine, Medicine.medicine_id == MedicineReminder.medicine_id)
        .where(MedicineReminder.patient_id == patient_id)
        .order_by(MedicineReminder.reminder_time)
    ).all()

    return [
        reminder_details(reminder, medicine)
        for reminder, medicine in rows
    ]


@router.patch("/{reminder_id}")
def update_reminder(
    reminder_id: int,
    data: MedicineReminderUpdate,
    user: User = Depends(require_roles(ROLE_PATIENT)),
    db: Session = Depends(get_db),
):
    patient_id = get_patient_id(user)

    reminder = db.scalar(
        select(MedicineReminder).where(
            MedicineReminder.reminder_id == reminder_id,
            MedicineReminder.patient_id == patient_id,
        )
    )

    if reminder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found",
        )

    changes = data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide reminder_time or is_active",
        )

    for field, value in changes.items():
        if value is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} cannot be empty",
            )
        setattr(reminder, field, value)

    db.commit()
    db.refresh(reminder)

    medicine = db.get(Medicine, reminder.medicine_id)
    return reminder_details(reminder, medicine)
