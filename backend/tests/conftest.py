import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["AUTO_CREATE_TABLES"] = "true"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["ENABLE_SCHEDULER"] = "false"
os.environ["AUTO_GENERATE_MEDIA"] = "false"
os.environ["EXTERNAL_BASE_DELAY"] = "0"
os.environ["EXTERNAL_MIN_INTERVAL"] = "0"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine

from app import models
from app.database import Base, get_db
from app.main import app
from app.security import hash_password

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestingSession() as s:
        for r in (models.ROLE_DOCTOR, models.ROLE_PATIENT, models.ROLE_ADMIN):
            s.add(models.Role(role_name=r))
        s.commit()
        yield s


@pytest.fixture()
def client(db, tmp_path):
    from app.config import get_settings
    get_settings().UPLOAD_DIR = str(tmp_path / "uploads")
    get_settings().MEDIA_DIR = str(tmp_path / "media")

    def _get_db():
        yield db
    app.dependency_overrides[get_db] = _get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# ---------- helpers ----------
def patient_payload(email="pat@example.com", name="Asha Rao"):
    return {"name": name, "email": email, "password": "Passw0rdX", "role": "Patient",
            "date_of_birth": "1995-04-12", "phone": "9876543210", "preferred_language": "Kannada",
            "address": "Bengaluru"}


def doctor_payload(email="doc@example.com", name="Dr Mehta", license_number="KMC1234"):
    return {"name": name, "email": email, "password": "Passw0rdX", "role": "Doctor",
            "specialization": "General Medicine", "qualification": "MBBS", "license_number": license_number}


def login(client, email, password="Passw0rdX"):
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def patient(client):
    r = client.post("/auth/register", json=patient_payload())
    assert r.status_code == 201, r.text
    return {"headers": login(client, "pat@example.com"), "user": r.json()}


@pytest.fixture()
def patient2(client):
    client.post("/auth/register", json=patient_payload("pat2@example.com", "Ravi K"))
    return {"headers": login(client, "pat2@example.com")}


@pytest.fixture()
def doctor(client):
    assert client.post("/auth/register", json=doctor_payload()).status_code == 201
    return {"headers": login(client, "doc@example.com")}


@pytest.fixture()
def doctor2(client):
    client.post("/auth/register", json=doctor_payload("doc2@example.com", "Dr Iyer", "KMC9999"))
    return {"headers": login(client, "doc2@example.com")}


@pytest.fixture()
def admin(client, db):
    role = db.query(models.Role).filter_by(role_name="Admin").one()
    db.add(models.User(name="Admin", email="admin@example.com", password_hash=hash_password("Passw0rdX"),
                       role_id=role.role_id))
    db.commit()
    return {"headers": login(client, "admin@example.com")}


def patient_id(client, doctor_headers, name_part="Asha"):
    r = client.get("/patients", params={"search": name_part}, headers=doctor_headers)
    return r.json()[0]["patient_id"]


def rx_payload(pid, **over):
    d = {"patient_id": pid, "medicine_name": "Paracetamol", "dosage": "500 mg", "frequency": "Twice daily",
         "duration": "5 days", "instructions": "After food", "prescription_date": "2026-10-20"}
    d.update(over)
    return d
