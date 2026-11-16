import pytest
from .conftest import patient_id, rx_payload


def test_doctor_creates_prescription_as_pending(client, patient, doctor):
    pid = patient_id(client, doctor["headers"])
    r = client.post("/prescriptions", json=rx_payload(pid), headers=doctor["headers"])
    assert r.status_code == 201
    b = r.json()
    assert b["verification_status"] == "Pending" and b["processing_status"] == "Pending Verification"
    assert b["status"] == "Active" and b["patient_name"] == "Asha Rao" and b["doctor_name"] == "Dr Mehta"


def test_dosage_text_preserved_exactly(client, patient, doctor):
    pid = patient_id(client, doctor["headers"])
    r = client.post("/prescriptions", json=rx_payload(pid, dosage="250 mg/5 ml"), headers=doctor["headers"])
    got = client.get(f"/prescriptions/{r.json()['prescription_id']}", headers=doctor["headers"]).json()
    assert got["dosage"] == "250 mg/5 ml"


def test_patient_and_admin_cannot_create(client, patient, admin, doctor):
    pid = patient_id(client, doctor["headers"])
    assert client.post("/prescriptions", json=rx_payload(pid), headers=patient["headers"]).status_code == 403
    assert client.post("/prescriptions", json=rx_payload(pid), headers=admin["headers"]).status_code == 403


@pytest.mark.parametrize("field", ["medicine_name", "dosage", "frequency", "duration", "prescription_date", "patient_id"])
def test_mandatory_fields_required(client, patient, doctor, field):
    pid = patient_id(client, doctor["headers"])
    p = rx_payload(pid); p.pop(field)
    assert client.post("/prescriptions", json=p, headers=doctor["headers"]).status_code == 422


@pytest.mark.parametrize("field", ["medicine_name", "dosage", "frequency", "duration"])
def test_blank_fields_rejected(client, patient, doctor, field):
    pid = patient_id(client, doctor["headers"])
    assert client.post("/prescriptions", json=rx_payload(pid, **{field: "   "}), headers=doctor["headers"]).status_code == 422


def test_future_date_and_unknown_patient_rejected(client, patient, doctor):
    pid = patient_id(client, doctor["headers"])
    assert client.post("/prescriptions", json=rx_payload(pid, prescription_date="2999-01-01"), headers=doctor["headers"]).status_code == 422
    assert client.post("/prescriptions", json=rx_payload(9999), headers=doctor["headers"]).status_code == 404


def test_patient_only_sees_verified_own_prescriptions(client, patient, patient2, doctor):
    pid = patient_id(client, doctor["headers"])
    rid = client.post("/prescriptions", json=rx_payload(pid), headers=doctor["headers"]).json()["prescription_id"]
    assert client.get("/prescriptions", headers=patient["headers"]).json() == []
    assert client.get(f"/prescriptions/{rid}", headers=patient["headers"]).status_code == 403
    client.post(f"/prescriptions/{rid}/verify", headers=doctor["headers"])
    assert len(client.get("/prescriptions", headers=patient["headers"]).json()) == 1
    assert client.get(f"/prescriptions/{rid}", headers=patient["headers"]).status_code == 200
    assert client.get(f"/prescriptions/{rid}", headers=patient2["headers"]).status_code == 403


def test_doctor_only_sees_own_prescriptions(client, patient, doctor, doctor2):
    pid = patient_id(client, doctor["headers"])
    rid = client.post("/prescriptions", json=rx_payload(pid), headers=doctor["headers"]).json()["prescription_id"]
    assert client.get(f"/prescriptions/{rid}", headers=doctor2["headers"]).status_code == 403
    assert client.get("/prescriptions", headers=doctor2["headers"]).json() == []
    assert len(client.get("/prescriptions", headers=doctor["headers"]).json()) == 1
    assert client.put(f"/prescriptions/{rid}", json={"dosage": "1 g"}, headers=doctor2["headers"]).status_code == 403
    assert client.post(f"/prescriptions/{rid}/verify", headers=doctor2["headers"]).status_code == 403


def test_admin_can_view_all_but_not_modify(client, patient, doctor, admin):
    pid = patient_id(client, doctor["headers"])
    rid = client.post("/prescriptions", json=rx_payload(pid), headers=doctor["headers"]).json()["prescription_id"]
    assert len(client.get("/prescriptions", headers=admin["headers"]).json()) == 1
    assert client.post(f"/prescriptions/{rid}/verify", headers=admin["headers"]).status_code == 403


def test_update_then_verify_then_locked(client, patient, doctor):
    pid = patient_id(client, doctor["headers"])
    rid = client.post("/prescriptions", json=rx_payload(pid), headers=doctor["headers"]).json()["prescription_id"]
    r = client.put(f"/prescriptions/{rid}", json={"dosage": "650 mg"}, headers=doctor["headers"])
    assert r.status_code == 200 and r.json()["dosage"] == "650 mg"
    v = client.post(f"/prescriptions/{rid}/verify", json={"action": "verify"}, headers=doctor["headers"]).json()
    assert v["verification_status"] == "Verified" and v["processing_status"] == "Verified"
    assert client.put(f"/prescriptions/{rid}", json={"dosage": "1 g"}, headers=doctor["headers"]).status_code == 409
    # status (e.g. Completed) may still change after verification
    assert client.put(f"/prescriptions/{rid}", json={"status": "Completed"}, headers=doctor["headers"]).status_code == 200


def test_reject(client, patient, doctor):
    pid = patient_id(client, doctor["headers"])
    rid = client.post("/prescriptions", json=rx_payload(pid), headers=doctor["headers"]).json()["prescription_id"]
    r = client.post(f"/prescriptions/{rid}/verify", json={"action": "reject"}, headers=doctor["headers"]).json()
    assert r["verification_status"] == "Rejected" and r["processing_status"] == "Rejected"


def test_update_cannot_blank_required_field(client, patient, doctor):
    pid = patient_id(client, doctor["headers"])
    rid = client.post("/prescriptions", json=rx_payload(pid), headers=doctor["headers"]).json()["prescription_id"]
    assert client.put(f"/prescriptions/{rid}", json={"dosage": None}, headers=doctor["headers"]).status_code == 422
    assert client.put(f"/prescriptions/{rid}", json={"dosage": ""}, headers=doctor["headers"]).status_code == 422


def test_missing_prescription_404(client, doctor):
    assert client.get("/prescriptions/9999", headers=doctor["headers"]).status_code == 404
