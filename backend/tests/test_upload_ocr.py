import io

import pytest
from app.services import ocr
from .conftest import patient_id

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 100
JPG = b"\xff\xd8\xff\xe0" + b"0" * 100
OCR_TEXT = "Dr Mehta\nTab Paracetamol 500 mg BD x 5 days after food\nCap Omeprazole 20 mg OD\n"

def make_pdf(text: str) -> bytes:
    """Build a minimal valid single-page PDF containing `text`."""
    stream = f"BT /F1 12 Tf 10 100 Td ({text}) Tj ET".encode()
    objs = [b"<</Type/Catalog/Pages 2 0 R>>", b"<</Type/Pages/Kids[3 0 R]/Count 1>>",
            b"<</Type/Page/Parent 2 0 R/MediaBox[0 0 400 200]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>",
            b"<</Length %d>>\nstream\n" % len(stream) + stream + b"\nendstream",
            b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>"]
    out, offsets = b"%PDF-1.4\n", []
    for i, o in enumerate(objs, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + o + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    out += b"".join(b"%010d 00000 n \n" % off for off in offsets)
    return out + b"trailer<</Root 1 0 R/Size %d>>\nstartxref\n%d\n%%%%EOF" % (len(objs) + 1, xref)


MINI_PDF = make_pdf("Tab Amoxicillin 250 mg TDS 7 days")


@pytest.fixture()
def fake_ocr(monkeypatch):
    monkeypatch.setattr(ocr, "extract_text", lambda path, file_type: OCR_TEXT)


def upload(client, headers, pid, name="rx.png", content=PNG, **extra):
    return client.post("/prescriptions/upload", headers=headers, data={"patient_id": str(pid), **extra},
                       files={"file": (name, io.BytesIO(content))})


def test_upload_extracts_medicines_and_awaits_verification(client, patient, doctor, fake_ocr):
    pid = patient_id(client, doctor["headers"])
    r = upload(client, doctor["headers"], pid)
    assert r.status_code == 201, r.text
    b = r.json()
    assert b["ocr_status"] == "success"
    assert b["processing_status"] == "Pending Verification" and b["verification_status"] == "Pending"
    assert b["files"][0]["upload_status"] == "Processed" and b["files"][0]["file_type"] == "png"
    names = [m["medicine_name"] for m in b["medicines"]]
    assert names == ["Paracetamol", "Omeprazole"]
    assert b["medicine_name"] == "Paracetamol" and b["dosage"] == "500 mg"  # header mirrors first medicine
    omep = b["medicines"][1]
    assert omep["extraction_status"] == "Needs Review" and omep["duration"] == "Not detected"


def test_stored_filename_is_not_client_name(client, patient, doctor, fake_ocr, db):
    from app.models import PrescriptionFile
    pid = patient_id(client, doctor["headers"])
    upload(client, doctor["headers"], pid, name="../../evil name.png")
    f = db.query(PrescriptionFile).one()
    assert "evil" not in f.stored_file_path and f.original_file_name == "evil name.png"


@pytest.mark.parametrize("name,content,code", [
    ("rx.exe", b"MZ" + b"0" * 50, 415),
    ("rx.txt", b"hello", 415),
    ("rx", PNG, 415),
    ("rx.png", JPG, 415),            # content does not match extension
    ("rx.pdf", PNG, 415),
    ("rx.png", b"", 400),
])
def test_file_validation(client, patient, doctor, fake_ocr, name, content, code):
    pid = patient_id(client, doctor["headers"])
    assert upload(client, doctor["headers"], pid, name=name, content=content).status_code == code


def test_oversize_file_rejected(client, patient, doctor, fake_ocr):
    pid = patient_id(client, doctor["headers"])
    big = PNG + b"0" * (5 * 1024 * 1024)
    assert upload(client, doctor["headers"], pid, content=big).status_code == 413


def test_upload_permissions_and_inputs(client, patient, doctor, fake_ocr):
    pid = patient_id(client, doctor["headers"])
    assert upload(client, patient["headers"], pid).status_code == 403
    assert client.post("/prescriptions/upload", data={"patient_id": str(pid)},
                       files={"file": ("a.png", io.BytesIO(PNG))}).status_code == 401
    assert upload(client, doctor["headers"], 9999).status_code == 404
    assert upload(client, doctor["headers"], pid, prescription_date="2999-01-01").status_code == 422


def test_ocr_failure_is_handled(client, patient, doctor, monkeypatch):
    def boom(path, file_type):
        raise ocr.OCRUnavailable("tesseract not installed")
    monkeypatch.setattr(ocr, "extract_text", boom)
    pid = patient_id(client, doctor["headers"])
    b = upload(client, doctor["headers"], pid).json()
    assert b["ocr_status"] == "failed" and b["processing_status"] == "Uploaded"
    assert b["files"][0]["upload_status"] == "Failed" and b["medicines"] == []
    # doctor falls back to manual entry, then can verify
    rid = b["prescription_id"]
    assert client.post(f"/prescriptions/{rid}/verify", headers=doctor["headers"]).status_code == 409
    m = client.post(f"/prescriptions/{rid}/medicines", headers=doctor["headers"], json={
        "medicine_name": "Paracetamol", "dosage": "500 mg", "frequency": "Twice daily", "duration": "5 days"})
    assert m.status_code == 201
    assert client.post(f"/prescriptions/{rid}/verify", headers=doctor["headers"]).status_code == 200


def test_no_medicines_found(client, patient, doctor, monkeypatch):
    monkeypatch.setattr(ocr, "extract_text", lambda p, t: "Just some handwriting with no drugs")
    pid = patient_id(client, doctor["headers"])
    b = upload(client, doctor["headers"], pid).json()
    assert b["ocr_status"] == "no_medicines_found" and b["processing_status"] == "Pending Verification"


def test_real_pdf_text_extraction(client, patient, doctor):
    """No mocking: embedded-text PDFs go through pypdf + the extraction rules."""
    pid = patient_id(client, doctor["headers"])
    b = upload(client, doctor["headers"], pid, name="rx.pdf", content=MINI_PDF).json()
    assert b["ocr_status"] == "success", b
    assert b["medicines"][0]["medicine_name"] == "Amoxicillin" and b["medicines"][0]["dosage"] == "250 mg"


def test_verification_blocked_until_missing_info_corrected(client, patient, doctor, fake_ocr):
    pid = patient_id(client, doctor["headers"])
    rid = upload(client, doctor["headers"], pid).json()["prescription_id"]
    h = doctor["headers"]
    assert client.post(f"/prescriptions/{rid}/verify", headers=h).status_code == 409
    meds = client.get(f"/prescriptions/{rid}/medicines", headers=h).json()
    needs = next(m for m in meds if m["extraction_status"] == "Needs Review")
    r = client.put(f"/prescriptions/{rid}/medicines/{needs['medicine_id']}", headers=h, json={"duration": "14 days"})
    assert r.status_code == 200 and r.json()["extraction_status"] == "Confirmed"
    v = client.post(f"/prescriptions/{rid}/verify", headers=h)
    assert v.status_code == 200
    body = v.json()
    assert body["verification_status"] == "Verified" and body["processing_status"] == "Verified"
    assert all(m["extraction_status"] == "Confirmed" for m in body["medicines"])
    # locked afterwards
    assert client.put(f"/prescriptions/{rid}/medicines/{needs['medicine_id']}", headers=h,
                      json={"dosage": "1 g"}).status_code == 409
    assert client.delete(f"/prescriptions/{rid}/medicines/{needs['medicine_id']}", headers=h).status_code == 409
    assert client.post(f"/prescriptions/{rid}/reprocess", headers=h).status_code == 409


def test_correcting_incorrect_medicine_updates_header(client, patient, doctor, fake_ocr):
    pid = patient_id(client, doctor["headers"])
    h = doctor["headers"]
    b = upload(client, h, pid).json()
    first = b["medicines"][0]["medicine_id"]
    client.put(f"/prescriptions/{b['prescription_id']}/medicines/{first}", headers=h,
               json={"medicine_name": "Dolo", "dosage": "650 mg"})
    got = client.get(f"/prescriptions/{b['prescription_id']}", headers=h).json()
    assert got["medicine_name"] == "Dolo" and got["dosage"] == "650 mg"


def test_medicine_validation(client, patient, doctor, fake_ocr):
    pid = patient_id(client, doctor["headers"])
    h = doctor["headers"]
    b = upload(client, h, pid).json()
    rid, mid = b["prescription_id"], b["medicines"][0]["medicine_id"]
    assert client.put(f"/prescriptions/{rid}/medicines/{mid}", headers=h, json={"dosage": ""}).status_code == 422
    assert client.put(f"/prescriptions/{rid}/medicines/{mid}", headers=h, json={"dosage": None}).status_code == 422
    assert client.put(f"/prescriptions/{rid}/medicines/9999", headers=h, json={"dosage": "1 g"}).status_code == 404
    assert client.post(f"/prescriptions/{rid}/medicines", headers=h, json={"medicine_name": "X"}).status_code == 422


def test_reprocess_replaces_medicines(client, patient, doctor, fake_ocr, monkeypatch):
    pid = patient_id(client, doctor["headers"])
    h = doctor["headers"]
    rid = upload(client, h, pid).json()["prescription_id"]
    monkeypatch.setattr(ocr, "extract_text", lambda p, t: "Tab Aspirin 75 mg OD 30 days")
    b = client.post(f"/prescriptions/{rid}/reprocess", headers=h).json()
    assert [m["medicine_name"] for m in b["medicines"]] == ["Aspirin"]


def test_file_and_medicine_access_control(client, patient, patient2, doctor, doctor2, admin, fake_ocr):
    pid = patient_id(client, doctor["headers"])
    rid = upload(client, doctor["headers"], pid).json()["prescription_id"]
    mid = client.get(f"/prescriptions/{rid}/medicines", headers=doctor["headers"]).json()[0]["medicine_id"]
    for path in (f"/prescriptions/{rid}/file", f"/prescriptions/{rid}/medicines"):
        assert client.get(path, headers=doctor["headers"]).status_code == 200
        assert client.get(path, headers=admin["headers"]).status_code == 200
        assert client.get(path, headers=doctor2["headers"]).status_code == 403
        assert client.get(path, headers=patient2["headers"]).status_code == 403
        assert client.get(path, headers=patient["headers"]).status_code == 403   # not verified yet
        assert client.get(path).status_code == 401
    assert client.put(f"/prescriptions/{rid}/medicines/{mid}", json={"dosage": "1 g"},
                      headers=doctor2["headers"]).status_code == 403
    assert client.put(f"/prescriptions/{rid}/medicines/{mid}", json={"dosage": "1 g"},
                      headers=patient["headers"]).status_code == 403
    # after verification the owning patient (only) can read
    client.put(f"/prescriptions/{rid}/medicines/{mid + 1}", headers=doctor["headers"], json={"duration": "5 days"})
    assert client.post(f"/prescriptions/{rid}/verify", headers=doctor["headers"]).status_code == 200
    assert client.get(f"/prescriptions/{rid}/medicines", headers=patient["headers"]).status_code == 200
    assert client.get(f"/prescriptions/{rid}/file", headers=patient["headers"]).status_code == 200
    assert client.get(f"/prescriptions/{rid}/file", headers=patient2["headers"]).status_code == 403


def test_manual_prescription_has_confirmed_medicine_row(client, patient, doctor):
    from .conftest import rx_payload
    pid = patient_id(client, doctor["headers"])
    b = client.post("/prescriptions", json=rx_payload(pid), headers=doctor["headers"]).json()
    assert len(b["medicines"]) == 1 and b["medicines"][0]["extraction_status"] == "Confirmed"
    # editing the header edits the medicine row too
    client.put(f"/prescriptions/{b['prescription_id']}", json={"dosage": "650 mg"}, headers=doctor["headers"])
    got = client.get(f"/prescriptions/{b['prescription_id']}", headers=doctor["headers"]).json()
    assert got["medicines"][0]["dosage"] == "650 mg"
