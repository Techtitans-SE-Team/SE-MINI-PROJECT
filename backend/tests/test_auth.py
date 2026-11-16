import pytest
from app import models
from .conftest import doctor_payload, login, patient_payload


def test_register_patient_and_doctor(client):
    r = client.post("/auth/register", json=patient_payload())
    assert r.status_code == 201 and r.json()["role_name"] == "Patient"
    assert "password" not in r.text and "password_hash" not in r.text
    r = client.post("/auth/register", json=doctor_payload())
    assert r.status_code == 201 and r.json()["role_name"] == "Doctor"


def test_password_is_hashed_in_db(client, db):
    client.post("/auth/register", json=patient_payload())
    u = db.query(models.User).filter_by(email="pat@example.com").one()
    assert u.password_hash != "Passw0rdX" and u.password_hash.startswith("$2")


def test_duplicate_email_rejected(client):
    client.post("/auth/register", json=patient_payload())
    r = client.post("/auth/register", json=patient_payload())
    assert r.status_code == 409


def test_email_is_case_insensitive(client):
    client.post("/auth/register", json=patient_payload("A@Example.com"))
    assert client.post("/auth/register", json=patient_payload("a@example.com")).status_code == 409
    assert client.post("/auth/login", json={"email": "A@EXAMPLE.COM", "password": "Passw0rdX"}).status_code == 200


def test_admin_cannot_self_register(client):
    p = patient_payload(); p["role"] = "Admin"
    assert client.post("/auth/register", json=p).status_code == 422


@pytest.mark.parametrize("field,value", [
    ("password", "short1A"), ("password", "alllowercase1"), ("password", "NoDigitsHere"),
    ("email", "not-an-email"), ("phone", "123"), ("name", "A"),
    ("date_of_birth", "2999-01-01"),
])
def test_invalid_patient_inputs(client, field, value):
    p = patient_payload(); p[field] = value
    assert client.post("/auth/register", json=p).status_code == 422


@pytest.mark.parametrize("missing", ["name", "email", "password", "date_of_birth", "phone", "preferred_language"])
def test_missing_patient_fields(client, missing):
    p = patient_payload(); p.pop(missing)
    assert client.post("/auth/register", json=p).status_code == 422


def test_doctor_requires_specialization(client):
    d = doctor_payload(); d.pop("specialization")
    assert client.post("/auth/register", json=d).status_code == 422


def test_duplicate_license_rejected(client):
    client.post("/auth/register", json=doctor_payload())
    assert client.post("/auth/register", json=doctor_payload("other@example.com")).status_code == 409


def test_login_success_returns_token_and_role(client, patient):
    r = client.post("/auth/login", json={"email": "pat@example.com", "password": "Passw0rdX"})
    body = r.json()
    assert r.status_code == 200 and body["role"] == "Patient" and body["access_token"]


def test_login_failures_are_indistinguishable(client, patient):
    wrong_pw = client.post("/auth/login", json={"email": "pat@example.com", "password": "Wrong123x"})
    no_user = client.post("/auth/login", json={"email": "ghost@example.com", "password": "Wrong123x"})
    assert wrong_pw.status_code == no_user.status_code == 401
    assert wrong_pw.json() == no_user.json()


def test_me_requires_valid_token(client, patient):
    assert client.get("/auth/me").status_code == 401
    assert client.get("/auth/me", headers={"Authorization": "Bearer garbage"}).status_code == 401
    assert client.get("/auth/me", headers=patient["headers"]).json()["email"] == "pat@example.com"
