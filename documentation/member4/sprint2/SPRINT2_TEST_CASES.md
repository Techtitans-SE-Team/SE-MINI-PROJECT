# Sprint 2 – Test Case Documentation

**Project:** Doctor Prescription to Multilingual Video Reminder and Instruction Generator
**Team:** TechTitans
**Role:** Member 4 – Testing and Quality Assurance
**Sprint:** Sprint 2
**Testing Type:** Functional, OCR, extraction and negative testing

---

## 1. Objective

The objective of Sprint 2 testing is to verify prescription image processing, scanned PDF processing, OCR text extraction, medicine information extraction and error handling.

Testing is performed without modifying the backend implementation.

## 2. Test Environment

| Component | Environment |
|---|---|
| Operating System | macOS |
| Python | 3.11 |
| Test Framework | pytest |
| OCR Engine | Tesseract 5.5.4 |
| PDF Processing | Poppler 26.11.0 |
| Image Processing | Pillow |
| Image OCR Library | pytesseract |
| PDF Libraries | pdf2image, pypdf |

## 3. Executed Test Cases

### TC-S2-01: Actual Prescription Image OCR

- **Objective:** Verify that Tesseract extracts text from a prescription image.
- **Input:** Sample PNG prescription image.
- **Steps:**
  1. Create a sample prescription image.
  2. Pass the image to the OCR service.
  3. Inspect the extracted text.
- **Expected Result:** Prescription text should be extracted correctly.
- **Actual Result:** Complete sample prescription text was extracted.
- **Status:** PASS
- **Execution Type:** Manual service-level test.

### TC-S2-02: Medicine Extraction from Image OCR

- **Objective:** Verify medicine information extraction from OCR output.
- **Input:** OCR text containing Amoxicillin and Paracetamol.
- **Steps:**
  1. Pass OCR output to the extraction module.
  2. Inspect medicine names, dosage, frequency and duration.
  3. Check the needs_review property.
- **Expected Result:** Both medicines and their details should be extracted correctly.
- **Actual Result:**

| Medicine | Dosage | Frequency | Duration | Needs Review |
|---|---|---|---|---|
| Amoxicillin | 250 mg | Three times daily | 7 days | False |
| Paracetamol | 500 mg | Twice daily | 5 days | False |

- **Status:** PASS
- **Execution Type:** Manual service-level test.

### TC-S2-03: Scanned PDF Embedded Text Verification

- **Objective:** Verify that the test PDF contains no embedded selectable text.
- **Steps:**
  1. Create a PDF containing the prescription as an image.
  2. Read the PDF using pypdf.
  3. Inspect the extracted embedded text.
- **Expected Result:** No embedded text should be available.
- **Actual Result:** Page 1 embedded text: ''.
- **Status:** PASS
- **Execution Type:** Manual test.

### TC-S2-04: Scanned PDF OCR Fallback

- **Objective:** Verify that scanned PDFs are processed using Poppler and Tesseract.
- **Steps:**
  1. Pass the scanned PDF to the OCR service.
  2. Verify that embedded text is unavailable.
  3. Inspect the OCR output.
  4. Pass the extracted text to the medicine extraction module.
- **Expected Result:** The scanned PDF should be processed and both medicines should be extracted.
- **Actual Result:** Amoxicillin and Paracetamol were extracted with the expected dosage, frequency and duration.
- **Status:** PASS
- **Execution Type:** Manual service-level test.

### TC-S2-05: Existing Automated Backend Test Suite

- **Objective:** Verify that existing backend functionality continues to pass its automated tests.
- **Steps:**
  1. Navigate to the backend directory.
  2. Execute `pytest -q`.
  3. Inspect the final test summary.
- **Expected Result:** All existing automated tests should pass.
- **Actual Result:** 84 passed, 0 failed, 1 warning.
- **Execution Time:** 75.84 seconds.
- **Status:** PASS
- **Execution Type:** Automated.

## 4. Additional Executed and Pending Test Cases

The following table records additional test execution results.

| Test ID | Test Scenario | Expected Result | Status |
|---|---|---|---|
| TC-S2-06 | Corrupted PDF processing | OCRUnavailable raised for corrupted PDF | PASS |
| TC-S2-07 | Invalid image processing | OCRUnavailable raised for invalid image | PASS |
| TC-S2-08 | Empty image processing | OCRUnavailable raised for empty image | PASS |
| TC-S2-09 | Prescription with missing dosage | Dosage marked Not detected and review required | PASS |
| TC-S2-10 | Prescription with missing frequency | Frequency marked Not detected and review required | PASS |
| TC-S2-11 | Decimal dosage extraction | 2.5 mg extracted correctly | PASS |
| TC-S2-12 | Multiple medicines with incomplete details | All three medicines extracted; incomplete records flagged | PASS |
| TC-S2-13 | Reprocessing after initial OCR failure | OCR recovery and Aspirin extraction verified | PASS |

## 5. Observations and Limitations

1. Actual image OCR successfully extracted the sample prescription text.
2. Scanned PDF processing successfully extracted text despite the absence of embedded PDF text.
3. Medicine names, dosage, frequency and duration were correctly extracted for both sample medicines.
4. The instruction "Take after food" was detected by OCR but was not associated with either medicine because it appeared on a separate line.
5. The image and scanned-PDF tests were conducted directly at the OCR service level. They do not establish complete end-to-end upload functionality.
6. The sample prescription used for testing is synthetic and does not represent a real clinical prescription.
7. The pending test cases must be executed before their results can be reported.

## 6. Conclusion

Sprint 2 testing has successfully verified actual image OCR, scanned PDF OCR fallback and medicine information extraction using sample prescription data.

The existing automated backend test suite also completed successfully with 84 passed tests and no failures.

Three negative OCR service-level tests were also executed successfully:
- Corrupted PDF processing.
- Invalid image processing.
- Empty image processing.

Additional extraction testing was completed successfully:
- Missing dosage detection.
- Missing frequency detection.
- Decimal dosage extraction.
- Multiple medicines with incomplete details.

Reprocessing after initial OCR failure was also tested successfully.
The dedicated Member 4 pytest test passed in 1.48 seconds.


## 7. Additional Automated Test

**Test file:** `backend/tests/test_member4_sprint2_reprocess.py`

**Test function:** `test_reprocess_after_initial_ocr_failure`

**Execution result:** 1 passed, 0 failed.

The test simulates an initial OCR failure, retries processing through the prescription reprocessing endpoint, and verifies successful extraction of Aspirin 75 mg.
