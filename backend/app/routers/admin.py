from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_roles
from ..models import ROLE_ADMIN, Doctor, Patient, Prescription, User
from ..schemas import UserOut

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_roles(ROLE_ADMIN))])


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.user_id)).all()


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    count = lambda model: db.scalar(select(func.count()).select_from(model))
    return {"users": count(User), "patients": count(Patient), "doctors": count(Doctor),
            "prescriptions": count(Prescription)}
