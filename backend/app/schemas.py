
import re
from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

PHONE_RE = re.compile(r"^\+?\d{10,14}$")


def _clean(v: str) -> str:
    return " ".join(v.split())


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    role: Literal["Patient", "Doctor"]
    date_of_birth: date | None = None
    phone: str | None = None
    preferred_language: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=255)
    specialization: str | None = Field(default=None, max_length=100)
    qualification: str | None = Field(default=None, max_length=100)
    license_number: str | None = Field(default=None, max_length=50)

    @field_validator("name")
    @classmethod
    def _name(cls, v):
        return _clean(v)

    @field_validator("email")
    @classmethod
    def _email(cls, v):
        return v.lower()

    @field_validator("password")
    @classmethod
    def _password(cls, v):
        if not (re.search(r"[a-z]", v) and re.search(r"[A-Z]", v) and re.search(r"\d", v)):
            raise ValueError("Password must contain an uppercase letter, a lowercase letter and a digit")
        return v

    @field_validator("phone")
    @classmethod
    def _phone(cls, v):
        if v is None:
            return v
        v = v.replace(" ", "").replace("-", "")
        if not PHONE_RE.match(v):
            raise ValueError("Phone must be 10-14 digits, optionally starting with +")
        return v

    @model_validator(mode="after")
    def _role_fields(self):
        if self.role == "Patient":
            missing = [f for f in ("date_of_birth", "phone", "preferred_language") if not getattr(self, f)]
            if missing:
                raise ValueError(f"Missing required patient fields: {', '.join(missing)}")
            if self.date_of_birth >= date.today():
                raise ValueError("date_of_birth must be in the past")
        else:
            if not self.specialization:
                raise ValueError("Missing required doctor field: specialization")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)

    @field_validator("email")
    @classmethod
    def _email(cls, v):
        return v.lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    role: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    name: str
    email: str
    role_name: str
    created_at: datetime | None = None


class PatientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    patient_id: int
    user_id: int
    name: str
    email: str
    date_of_birth: date
    phone: str
    preferred_language: str
    address: str | None = None
    status: str


class PatientBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    patient_id: int
    name: str
    preferred_language: str


class PatientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    date_of_birth: date | None = None
    phone: str | None = None
    preferred_language: str | None = Field(default=None, min_length=1, max_length=50)
    address: str | None = Field(default=None, max_length=255)

    @field_validator("phone")
    @classmethod
    def _phone(cls, v):
        if v is None:
            return v
        v = v.replace(" ", "").replace("-", "")
        if not PHONE_RE.match(v):
            raise ValueError("Phone must be 10-14 digits, optionally starting with +")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def _dob(cls, v):
        if v is not None and v >= date.today():
            raise ValueError("date_of_birth must be in the past")
        return v


class DoctorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    doctor_id: int
    user_id: int
    specialization: str
    qualification: str | None = None
    license_number: str | None = None


# ---------------- Prescriptions ----------------

class _MedicineFields(BaseModel):
    medicine_name: str = Field(min_length=1, max_length=150)
    dosage: str = Field(min_length=1, max_length=100)
    frequency: str = Field(min_length=1, max_length=100)
    duration: str = Field(min_length=1, max_length=100)
    instructions: str | None = None

    @field_validator("medicine_name", "dosage", "frequency", "duration")
    @classmethod
    def _not_blank(cls, v):
        v = _clean(v)
        if not v:
            raise ValueError("must not be blank")
        return v


class PrescriptionCreate(_MedicineFields):
    patient_id: int
    prescription_date: date

    @field_validator("prescription_date")
    @classmethod
    def _not_future(cls, v):
        if v > date.today():
            raise ValueError("prescription_date cannot be in the future")
        return v


class PrescriptionUpdate(BaseModel):
    medicine_name: str | None = Field(default=None, min_length=1, max_length=150)
    dosage: str | None = Field(default=None, min_length=1, max_length=100)
    frequency: str | None = Field(default=None, min_length=1, max_length=100)
    duration: str | None = Field(default=None, min_length=1, max_length=100)
    instructions: str | None = None
    status: Literal["Active", "Completed", "Cancelled"] | None = None


class VerifyRequest(BaseModel):
    action: Literal["verify", "reject"] = "verify"


class MedicineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    medicine_id: int
    prescription_id: int
    medicine_name: str
    dosage: str
    frequency: str
    duration: str
    instructions: str | None = None
    extraction_status: str


class MedicineCreate(_MedicineFields):
    pass


class MedicineUpdate(BaseModel):
    medicine_name: str | None = Field(default=None, min_length=1, max_length=150)
    dosage: str | None = Field(default=None, min_length=1, max_length=100)
    frequency: str | None = Field(default=None, min_length=1, max_length=100)
    duration: str | None = Field(default=None, min_length=1, max_length=100)
    instructions: str | None = None


class FileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    file_id: int
    prescription_id: int
    original_file_name: str
    file_type: str
    file_size: int | None = None
    upload_date: datetime | None = None
    upload_status: str


class PrescriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    prescription_id: int
    patient_id: int
    doctor_id: int
    patient_name: str
    doctor_name: str
    medicine_name: str
    dosage: str
    frequency: str
    duration: str
    instructions: str | None = None
    prescription_date: date
    verification_status: str
    processing_status: str
    status: str
    created_at: datetime | None = None
    medicines: list[MedicineOut] = []
    files: list[FileOut] = []


class UploadResponse(PrescriptionOut):
    ocr_status: Literal["success", "no_medicines_found", "failed"]
    message: str


# ---------------- Medicine Reminders ----------------

class MedicineReminderCreate(BaseModel):
    medicine_id: int
    reminder_time: time


class MedicineReminderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    reminder_id: int
    medicine_id: int
    patient_id: int
    reminder_time: time
    is_active: bool
    created_at: datetime | None = None


class MedicineReminderUpdate(BaseModel):
    reminder_time: time | None = None
    is_active: bool | None = None
