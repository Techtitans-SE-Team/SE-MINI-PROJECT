from .conftest import patient_id, rx_payload


def test_patient_profile_get_and_update(client, patient):
    r = client.get("/patients/me", headers=patient["headers"])
    assert r.status_code == 200 and r.json()["preferred_language"] == "Kannada"
    r = client.put("/patients/me", json={"phone": "+919000000001", "preferred_language": "Hindi"},
                   headers=patient["headers"])
    assert r.status_code == 200 and r.json()["preferred_language"] == "Hindi"


def test_patient_update_validation(client, patient):
    h = patient["headers"]
    assert client.put("/patients/me", json={"phone": "abc"}, headers=h).status_code == 422
    assert client.put("/patients/me", json={"phone": None}, headers=h).status_code == 422
    assert client.put("/patients/me", json={"date_of_birth": "2999-01-01"}, headers=h).status_code == 422


def test_endpoints_require_authentication(client):
    for path in ("/patients/me", "/patients", "/prescriptions", "/admin/users"):
        assert client.get(path).status_code == 401


def test_doctor_cannot_use_patient_only_endpoint(client, doctor):
    assert client.get("/patients/me", headers=doctor["headers"]).status_code == 403


def test_patient_cannot_list_patients_or_admin(client, patient):
    assert client.get("/patients", headers=patient["headers"]).status_code == 403
    assert client.get("/admin/users", headers=patient["headers"]).status_code == 403


def test_doctor_cannot_access_admin(client, doctor):
    assert client.get("/admin/stats", headers=doctor["headers"]).status_code == 403


def test_admin_access(client, admin, patient, doctor):
    assert len(client.get("/admin/users", headers=admin["headers"]).json()) >= 3
    assert client.get("/admin/stats", headers=admin["headers"]).json()["patients"] == 1


def test_patient_cannot_read_other_patient(client, patient, patient2, doctor):
    other_id = patient_id(client, doctor["headers"], "Ravi")
    assert client.get(f"/patients/{other_id}", headers=patient["headers"]).status_code == 403


def test_doctor_sees_patient_profile_only_after_prescribing(client, patient, doctor, doctor2):
    pid = patient_id(client, doctor["headers"])
    assert client.get(f"/patients/{pid}", headers=doctor["headers"]).status_code == 403
    client.post("/prescriptions", json=rx_payload(pid), headers=doctor["headers"])
    assert client.get(f"/patients/{pid}", headers=doctor["headers"]).status_code == 200
    assert client.get(f"/patients/{pid}", headers=doctor2["headers"]).status_code == 403


def test_unknown_patient_404(client, admin):
    assert client.get("/patients/9999", headers=admin["headers"]).status_code == 404
