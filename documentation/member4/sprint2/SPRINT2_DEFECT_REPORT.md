# Sprint 2 – Defect and Observation Report

**Project:** Doctor Prescription to Multilingual Video Reminder and Instruction Generator

**Team:** TechTitans

**Role:** Member 4 – Testing and Quality Assurance

**Sprint:** Sprint 2

## 1. Purpose

This report records defects, warnings, limitations and observations identified during Sprint 2 testing.

## 2. Defect Summary

| Category | Count |
|---|---:|
| Confirmed application defects | 0 |
| Test failures | 0 |
| Observations requiring review | 1 |
| Environment warnings | 1 |

## 3. Observations

### OBS-S2-01: Instructions on Separate Lines

**Observation:** The OCR service successfully recognized the instruction "Take after food". However, the extraction module did not associate it with either medicine because the instruction appeared on a separate line.

**Expected Behaviour:** Relevant prescription instructions should be associated with the appropriate medicine.

**Actual Behaviour:** The instruction was detected by OCR but not included in the extracted medicine records.

**Severity:** To be assessed.

**Status:** Open – Requires review.

**Evidence:** Actual image OCR and medicine extraction test output.

## 4. Environment Warning

### WARN-S2-01: Starlette/AnyIO Deprecation Warning

**Observation:** The automated test suite reported a deprecation warning concerning `anyio.abc.BlockingPortal`.

**Impact:** No test failures were caused by this warning.

**Status:** Observed – No corrective change made.

## 5. Testing Limitations

1. OCR image and scanned-PDF tests were conducted at service level rather than through the complete application workflow.
2. Synthetic prescription data was used.
3. Production MySQL integration was not established by the SQLite-based automated test suite.
4. Translation, multilingual video generation and reminder delivery were not verified in this OCR testing cycle.

## 6. Conclusion

No confirmed application defects were identified during the executed Sprint 2 tests.

One extraction limitation and one environment deprecation warning were recorded for future review.

All 13 documented test cases passed, and the complete backend automated test suite reported 85 passed tests with zero failures.
