from datetime import datetime, time

import pytest

from app.models import InstructionMedia, Notification
from app.services.scheduler import process_due_reminders, suggest_times
from tests.conftest import patient_id, rx_payload


@pytest.mark.parametrize("freq,expected", [
    ("1-0-1", [time(8), time(21)]), ("1-1-1", [time(8), time(14), time(21)]), ("0-0-1", [time(21)]),
    ("Twice daily", [time(8), time(20)]), ("BD", [time(8), time(20)]), ("TDS", [time(8), time(14), time(20)]),
    ("Once daily", [time(8)]), ("OD", [time(8)]), ("at night", [time(21)]), ("3 times a day", [time(8), time(14), time(20)]),
    ("4 times daily", [time(8), time(12), time(16), time(20)]), ("as needed", []), ("", [])])
def test_suggest_times(freq, expected):
    assert suggest_times(freq) == expected


@pytest.fixture()
def rx(client, doctor, patient):
    pid = patient_id(client, doctor["headers"])
    r = client.post("/prescriptions", json=rx_payload(pid, frequency="Twice daily"), headers=doctor["headers"]).json()
    return r["prescription_id"], r["medicines"][0]["medicine_id"]


@pytest.fixture()
def verified_rx(client, doctor, rx):
    assert client.post(f"/prescriptions/{rx[0]}/verify", headers=doctor["headers"]).status_code == 200
    return rx


def test_reminder_requires_verified_prescription(client, patient, rx):
    r = client.post("/reminders", json={"medicine_id": rx[1], "reminder_time": "08:00:00"}, headers=patient["headers"])
    assert r.status_code == 404


def test_create_list_patch_delete_reminder(client, patient, verified_rx):
    h = patient["headers"]
    r = client.post("/reminders", json={"medicine_id": verified_rx[1], "reminder_time": "08:30:00"}, headers=h)
    assert r.status_code == 201 and r.json()["medicine_name"] == "Paracetamol"
    rid = r.json()["reminder_id"]
    assert client.post("/reminders", json={"medicine_id": verified_rx[1], "reminder_time": "08:30:00"}, headers=h).status_code == 409
    assert len(client.get("/reminders", headers=h).json()) == 1
    assert client.patch(f"/reminders/{rid}", json={"is_active": False}, headers=h).json()["is_active"] is False
    assert client.patch(f"/reminders/{rid}", json={}, headers=h).status_code == 400
    assert client.delete(f"/reminders/{rid}", headers=h).status_code == 204
    assert client.get("/reminders", headers=h).json() == []


def test_reminders_are_private_and_patient_only(client, patient, patient2, doctor, verified_rx):
    rid = client.post("/reminders", json={"medicine_id": verified_rx[1], "reminder_time": "09:00:00"},
                      headers=patient["headers"]).json()["reminder_id"]
    assert client.patch(f"/reminders/{rid}", json={"is_active": False}, headers=patient2["headers"]).status_code == 404
    assert client.delete(f"/reminders/{rid}", headers=patient2["headers"]).status_code == 404
    assert client.get("/reminders", headers=doctor["headers"]).status_code == 403
    assert client.get("/reminders").status_code == 401


def test_auto_schedule_from_frequency(client, patient, verified_rx):
    r = client.post(f"/reminders/auto/{verified_rx[0]}", headers=patient["headers"])
    assert r.status_code == 201
    assert [x["reminder_time"] for x in r.json()["created"]] == ["08:00:00", "20:00:00"]
    again = client.post(f"/reminders/auto/{verified_rx[0]}", headers=patient["headers"]).json()
    assert again["created"] == []                                  # idempotent


def test_auto_schedule_flags_unknown_frequency(client, doctor, patient):
    pid = patient_id(client, doctor["headers"])
    rx = client.post("/prescriptions", json=rx_payload(pid, frequency="when required"), headers=doctor["headers"]).json()
    client.post(f"/prescriptions/{rx['prescription_id']}/verify", headers=doctor["headers"])
    r = client.post(f"/reminders/auto/{rx['prescription_id']}", headers=patient["headers"]).json()
    assert r["created"] == [] and r["needs_manual_time"] == ["Paracetamol"]


def test_auto_schedule_blocked_for_unverified(client, patient, rx):
    assert client.post(f"/reminders/auto/{rx[0]}", headers=patient["headers"]).status_code == 404


def test_due_notifications_created_once_per_day(client, db, patient, verified_rx):
    h = patient["headers"]
    client.post("/reminders", json={"medicine_id": verified_rx[1], "reminder_time": "08:00:00"}, headers=h)
    client.post("/reminders", json={"medicine_id": verified_rx[1], "reminder_time": "20:00:00"}, headers=h)

    assert process_due_reminders(db, now=datetime(2026, 11, 18, 7, 0)) == 0          # nothing due yet
    assert process_due_reminders(db, now=datetime(2026, 11, 18, 9, 0)) == 1          # 08:00 is due
    assert process_due_reminders(db, now=datetime(2026, 11, 18, 9, 1)) == 0          # not duplicated
    assert process_due_reminders(db, now=datetime(2026, 11, 18, 21, 0)) == 1         # 20:00 now due
    assert process_due_reminders(db, now=datetime(2026, 11, 19, 8, 5)) == 1          # next day again

    notes = client.get("/notifications", headers=h).json()
    assert len(notes) == 3 and "Paracetamol" in notes[0]["message"]


def test_inactive_reminder_creates_no_notification(client, db, patient, verified_rx):
    h = patient["headers"]
    rid = client.post("/reminders", json={"medicine_id": verified_rx[1], "reminder_time": "08:00:00"}, headers=h).json()["reminder_id"]
    client.patch(f"/reminders/{rid}", json={"is_active": False}, headers=h)
    assert process_due_reminders(db, now=datetime(2026, 11, 18, 12, 0)) == 0


def test_notification_uses_translated_text_and_links_media(client, db, patient, verified_rx):
    h = patient["headers"]
    db.add(InstructionMedia(prescription_id=verified_rx[0], medicine_id=verified_rx[1], language_code="kn",
                            language_name="Kannada", source_text="Take", translated_text="ಮಾತ್ರೆ ತೆಗೆದುಕೊಳ್ಳಿ"))
    db.commit()
    client.post("/reminders", json={"medicine_id": verified_rx[1], "reminder_time": "08:00:00"}, headers=h)
    process_due_reminders(db, now=datetime(2026, 11, 18, 8, 1))
    n = client.get("/notifications", headers=h).json()[0]
    assert n["message"] == "ಮಾತ್ರೆ ತೆಗೆದುಕೊಳ್ಳಿ" and n["media_id"] is not None


def test_notification_read_and_privacy(client, db, patient, patient2, verified_rx):
    h = patient["headers"]
    client.post("/reminders", json={"medicine_id": verified_rx[1], "reminder_time": "00:00:00"}, headers=h)
    assert client.post("/notifications/check", headers=h).json()["created"] == 1       # frontend polling endpoint
    nid = client.get("/notifications?unread_only=true", headers=h).json()[0]["notification_id"]
    assert client.post(f"/notifications/{nid}/read", headers=patient2["headers"]).status_code == 404
    assert client.post(f"/notifications/{nid}/read", headers=h).json()["status"] == "Read"
    assert client.get("/notifications?unread_only=true", headers=h).json() == []
    assert db.query(Notification).count() == 1
