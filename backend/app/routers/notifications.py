from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_roles
from ..models import ROLE_PATIENT, Notification, User
from ..schemas import NotificationOut
from ..services.scheduler import process_due_reminders
from .reminders import get_patient_id

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(unread_only: bool = False, user: User = Depends(require_roles(ROLE_PATIENT)),
                       db: Session = Depends(get_db)):
    stmt = select(Notification).where(Notification.patient_id == get_patient_id(user))
    if unread_only:
        stmt = stmt.where(Notification.status == "Unread")
    return db.scalars(stmt.order_by(Notification.notification_id.desc())).all()


@router.post("/check")
def check_now(user: User = Depends(require_roles(ROLE_PATIENT)), db: Session = Depends(get_db)):
    """Create notifications for reminders that are due right now (the frontend can poll this every minute)."""
    return {"created": process_due_reminders(db, patient_id=get_patient_id(user))}


@router.post("/{notification_id}/read", response_model=NotificationOut)
def mark_read(notification_id: int, user: User = Depends(require_roles(ROLE_PATIENT)), db: Session = Depends(get_db)):
    n = db.scalar(select(Notification).where(Notification.notification_id == notification_id,
                                             Notification.patient_id == get_patient_id(user)))
    if n is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")
    n.status = "Read"
    db.commit()
    db.refresh(n)
    return n
