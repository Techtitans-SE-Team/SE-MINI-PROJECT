import io

from app.services import ocr
from .conftest import patient_id


def test_reprocess_after_initial_ocr_failure(client, patient, doctor, monkeypatch):
    # First OCR attempt fails
    def failed_ocr(path, file_type):
        raise ocr.OCRUnavailable("Simulated initial OCR failure")

    monkeypatch.setattr(ocr, "extract_text", failed_ocr)

    pid = patient_id(client, doctor["headers"])

    response = client.post(
        "/prescriptions/upload",
        headers=doctor["headers"],
        data={"patient_id": str(pid)},
        files={
            "file": (
                "recovery_test.png",
                io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"0" * 100),
            )
        },
    )

    assert response.status_code == 201, response.text

    initial = response.json()
    prescription_id = initial["prescription_id"]

    assert initial["ocr_status"] == "failed"
    assert initial["processing_status"] == "Uploaded"
    assert initial["files"][0]["upload_status"] == "Failed"
    assert initial["medicines"] == []

    # Second OCR attempt succeeds
    monkeypatch.setattr(
        ocr,
        "extract_text",
        lambda path, file_type: "Tab Aspirin 75 mg OD 30 days",
    )

    reprocess = client.post(
        f"/prescriptions/{prescription_id}/reprocess",
        headers=doctor["headers"],
    )

    assert reprocess.status_code == 200, reprocess.text

    result = reprocess.json()

    assert result["ocr_status"] == "success"
    assert result["processing_status"] == "Pending Verification"
    assert len(result["medicines"]) == 1
    assert result["medicines"][0]["medicine_name"] == "Aspirin"
    assert result["medicines"][0]["dosage"] == "75 mg"
