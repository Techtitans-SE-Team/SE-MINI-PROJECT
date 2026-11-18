# Sprint 2 – Test Execution Report

**Project:** Doctor Prescription to Multilingual Video Reminder and Instruction Generator

**Team:** TechTitans

**Role:** Member 4 – Testing and Quality Assurance

**Sprint:** Sprint 2

## 1. Objective

This report records the execution results of Sprint 2 testing, covering OCR processing, scanned PDF handling, medicine information extraction, error handling and prescription reprocessing.

## 2. Test Environment

| Component | Details |
|---|---|
| Operating System | macOS |
| Python | 3.11.18 |
| pytest | 8.3.4 |
| Tesseract | 5.5.4 |
| Poppler | 26.11.0 |
| Image OCR | pytesseract, Pillow |
| PDF Processing | pdf2image, pypdf |

## 3. Test Execution Summary

| Metric | Result |
|---|---:|
| Documented test cases | 13 |
| Passed | 13 |
| Failed | 0 |
| Pending | 0 |

All 13 documented test cases passed.

## 4. Test Execution Results

| Test ID | Test Scenario | Result |
|---|---|---|
| TC-S2-01 | Actual prescription image OCR | PASS |
| TC-S2-02 | Medicine extraction from image OCR | PASS |
| TC-S2-03 | Scanned PDF embedded text verification | PASS |
| TC-S2-04 | Scanned PDF OCR fallback | PASS |
| TC-S2-05 | Existing automated backend test suite | PASS |
| TC-S2-06 | Corrupted PDF processing | PASS |
| TC-S2-07 | Invalid image processing | PASS |
| TC-S2-08 | Empty image processing | PASS |
| TC-S2-09 | Missing dosage detection | PASS |
| TC-S2-10 | Missing frequency detection | PASS |
| TC-S2-11 | Decimal dosage extraction | PASS |
| TC-S2-12 | Multiple medicines with incomplete details | PASS |
| TC-S2-13 | Reprocessing after initial OCR failure | PASS |

## 5. Automated Test Suite Results

The complete backend test suite was executed using:

`pytest -q`

**Final result:**
- Passed: 85
- Failed: 0
- Warnings: 1
- Execution time: 76.88 seconds

The warning was a Starlette/AnyIO deprecation warning concerning `anyio.abc.BlockingPortal`. It did not cause any test failures.

A separate Member 4 recovery test was also executed:

**Test file:** `tests/test_member4_sprint2_reprocess.py`

**Test function:** `test_reprocess_after_initial_ocr_failure`

**Result:** 1 passed in 1.48 seconds.

## 6. Key Findings

1. Tesseract successfully extracted text from the sample prescription image.
2. Poppler and Tesseract successfully processed a scanned PDF with no embedded text.
3. Medicine names, dosage, frequency and duration were correctly extracted from the test samples.
4. Missing medicine information was identified and flagged for review.
5. Decimal dosage values were preserved correctly.
6. Corrupted PDFs, invalid images and empty images were handled through OCRUnavailable exceptions.
7. Reprocessing after an initial OCR failure successfully recovered and extracted Aspirin 75 mg.

## 7. Observations and Limitations

1. The instruction "Take after food" was detected by OCR but was not associated with individual medicines because it appeared on a separate line.
2. Image and scanned-PDF tests were conducted directly at the OCR service level and do not establish complete end-to-end upload functionality.
3. The test prescription data was synthetic.
4. The automated suite uses its configured test database and does not establish production MySQL integration.
5. Translation, multilingual video generation and reminder delivery were not verified as part of these OCR tests.

## 8. Conclusion

Sprint 2 testing successfully verified the selected OCR, extraction, error-handling and reprocessing scenarios.

All 13 documented test cases passed, and the complete backend automated test suite finished with 85 passed tests and zero failures.

The observed limitations have been recorded for further review and improvement.
