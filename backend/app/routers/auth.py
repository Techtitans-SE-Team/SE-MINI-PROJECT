from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Doctor, Patient, Role, User
from ..schemas import LoginRequest, RegisterRequest, TokenResponse, UserOut
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a Patient or Doctor. Admin accounts cannot be self-registered."""
    if db.scalar(select(User).where(User.email == data.email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email is already registered")
    role = db.scalar(select(Role).where(Role.role_name == data.role))
    if role is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Roles are not initialised in the database")
    if data.role == "Doctor" and data.license_number and db.scalar(
            select(Doctor).where(Doctor.license_number == data.license_number)):
        raise HTTPException(status.HTTP_409_CONFLICT, "License number is already registered")

    user = User(name=data.name, email=data.email, password_hash=hash_password(data.password), role_id=role.role_id)
    try:
        db.add(user)
        db.flush()
        if data.role == "Patient":
            db.add(Patient(user_id=user.user_id, date_of_birth=data.date_of_birth, phone=data.phone,
                           preferred_language=data.preferred_language, address=data.address))
        else:
            db.add(Doctor(user_id=user.user_id, specialization=data.specialization,
                          qualification=data.qualification, license_number=data.license_number))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Could not register: duplicate or invalid data")
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email))
    # same message for unknown email / wrong password: no account enumeration
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    token = create_access_token(user.user_id, user.role_name)
    return TokenResponse(access_token=token, user_id=user.user_id, name=user.name, role=user.role_name)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
