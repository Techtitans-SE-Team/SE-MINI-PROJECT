
"""ORM models mapped to the MySQL schema in /database/schema (Member 3).
Enum-like columns are plain strings validated in the API layer."""
from datetime import date, datetime, time

from sqlalchemy import (
    BigInteger,
    UniqueConstraint,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

# ---- allowed values (mirror the SQL ENUMs) ----
ROLE_DOCTOR, ROLE_PATIENT, ROLE_ADMIN = "Doctor", "Patient", "Admin"

VERIFICATION_PENDING, VERIFICATION_VERIFIED, VERIFICATION_REJECTED = "Pending", "Verified", "Rejected"
PROC_UPLOADED, PROC_PROCESSING = "Uploaded", "Processing"
PROC_PENDING_VERIFICATION, PROC_VERIFIED, PROC_REJECTED = "Pending Verification", "Verified", "Rejected"
EXTRACTED, NEEDS_REVIEW, CONFIRMED = "Extracted", "Needs Review", "Confirmed"
FILE_UPLOADED, FILE_PROCESSING, FILE_PROCESSED, FILE_FAILED = "Uploaded", "Processing", "Processed", "Failed"


class Role(Base):
    __tablename__ = "roles"
    role_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)


class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.role_id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    role: Mapped[Role] = relationship(lazy="joined")
    patient: Mapped["Patient | None"] = relationship(back_populates="user", uselist=False)
    doctor: Mapped["Doctor | None"] = relationship(back_populates="user", uselist=False)

    @property
    def role_name(self) -> str:
        return self.role.role_name


class Patient(Base):
    __tablename__ = "patients"
    patient_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), unique=True, nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="Active")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped[User] = relationship(back_populates="patient")

    @property
    def name(self) -> str:
        return self.user.name

    @property
    def email(self) -> str:
        return self.user.email


class Doctor(Base):
    __tablename__ = "doctors"
    doctor_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), unique=True, nullable=False)
    specialization: Mapped[str] = mapped_column(String(100), nullable=False)
    qualification: Mapped[str | None] = mapped_column(String(100))
    license_number: Mapped[str | None] = mapped_column(String(50), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped[User] = relationship(back_populates="doctor")


class Prescription(Base):
    __tablename__ = "prescriptions"
    prescription_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id"), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.doctor_id"), nullable=False)
    medicine_name: Mapped[str] = mapped_column(String(150), nullable=False)
    dosage: Mapped[str] = mapped_column(String(100), nullable=False)
    frequency: Mapped[str] = mapped_column(String(100), nullable=False)
    duration: Mapped[str] = mapped_column(String(100), nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text)
    prescription_date: Mapped[date] = mapped_column(Date, nullable=False)
    verification_status: Mapped[str] = mapped_column(String(20), default=VERIFICATION_PENDING)
    processing_status: Mapped[str] = mapped_column(String(30), nullable=False, default=PROC_PENDING_VERIFICATION)
    status: Mapped[str] = mapped_column(String(20), default="Active")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    patient: Mapped[Patient] = relationship()
    doctor: Mapped[Doctor] = relationship()
    medicines: Mapped[list["Medicine"]] = relationship(
        back_populates="prescription", cascade="all, delete-orphan", order_by="Medicine.medicine_id")
    files: Mapped[list["PrescriptionFile"]] = relationship(
        back_populates="prescription", cascade="all, delete-orphan")

    @property
    def patient_name(self) -> str:
        return self.patient.user.name

    @property
    def doctor_name(self) -> str:
        return self.doctor.user.name


class Medicine(Base):
    __tablename__ = "medicines"
    medicine_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prescription_id: Mapped[int] = mapped_column(ForeignKey("prescriptions.prescription_id", ondelete="CASCADE"), nullable=False)
    medicine_name: Mapped[str] = mapped_column(String(150), nullable=False)
    dosage: Mapped[str] = mapped_column(String(100), nullable=False)
    frequency: Mapped[str] = mapped_column(String(100), nullable=False)
    duration: Mapped[str] = mapped_column(String(100), nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text)
    extraction_status: Mapped[str] = mapped_column(String(20), default=EXTRACTED)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    prescription: Mapped[Prescription] = relationship(back_populates="medicines")


class PrescriptionFile(Base):
    __tablename__ = "prescription_files"
    file_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prescription_id: Mapped[int] = mapped_column(ForeignKey("prescriptions.prescription_id", ondelete="CASCADE"), nullable=False)
    original_file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    upload_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    upload_status: Mapped[str] = mapped_column(String(20), default=FILE_UPLOADED)

    prescription: Mapped[Prescription] = relationship(back_populates="files")


class MedicineReminder(Base):
    __tablename__ = "medicine_reminders"

    reminder_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    medicine_id: Mapped[int] = mapped_column(
        ForeignKey("medicines.medicine_id", ondelete="CASCADE"),
        nullable=False
    )
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.patient_id", ondelete="CASCADE"),
        nullable=False
    )
    reminder_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class InstructionMedia(Base):
    """Translated instruction + audio + video generated for one medicine in one language."""
    __tablename__ = "instruction_media"
    __table_args__ = (UniqueConstraint("medicine_id", "language_code", name="uq_media_medicine_language"),)

    media_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prescription_id: Mapped[int] = mapped_column(ForeignKey("prescriptions.prescription_id", ondelete="CASCADE"), nullable=False)
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.medicine_id", ondelete="CASCADE"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(10), nullable=False)
    language_name: Mapped[str] = mapped_column(String(50), nullable=False)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    translated_text: Mapped[str] = mapped_column(Text, nullable=False)
    translated: Mapped[bool] = mapped_column(Boolean, default=True)
    audio_path: Mapped[str | None] = mapped_column(String(500))
    video_path: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="Completed")  # Completed / Partial / Failed
    message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    prescription: Mapped[Prescription] = relationship()
    medicine: Mapped[Medicine] = relationship()

    @property
    def has_audio(self) -> bool:
        return bool(self.audio_path)

    @property
    def has_video(self) -> bool:
        return bool(self.video_path)


class Notification(Base):
    """In-app notification created when a reminder time is reached (one per reminder per day)."""
    __tablename__ = "notifications"
    __table_args__ = (UniqueConstraint("reminder_id", "notify_date", name="uq_notification_reminder_day"),)

    notification_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.patient_id", ondelete="CASCADE"), nullable=False)
    reminder_id: Mapped[int] = mapped_column(ForeignKey("medicine_reminders.reminder_id", ondelete="CASCADE"), nullable=False)
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.medicine_id", ondelete="CASCADE"), nullable=False)
    media_id: Mapped[int | None] = mapped_column(ForeignKey("instruction_media.media_id", ondelete="SET NULL"))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notify_date: Mapped[date] = mapped_column(Date, nullable=False)
    reminder_time: Mapped[time] = mapped_column(Time, nullable=False)
    status: Mapped[str] = mapped_column(String(10), default="Unread")  # Unread / Read
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
