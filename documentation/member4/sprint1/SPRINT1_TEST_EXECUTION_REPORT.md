# Sprint 1 Test Execution Report

**Project:** Doctor Prescription to Multilingual Video Reminder and Instruction Generator  
**Scope:** User-reported execution of the existing backend pytest suite and verified mappings to Sprint 1 formal cases  
**Execution date:** Not supplied  
**Evidence source:** Execution summary supplied by the user; no raw console output, JUnit XML, or per-test report was provided.

## 1. Reported execution result

| Item | Actual result |
|---|---:|
| Python | 3.11.18 |
| pytest | 8.3.4 |
| Pytest test instances passed | 84 |
| Pytest test instances failed | 0 |
| Deprecation warnings | 1 |
| Elapsed execution time | 75.76 seconds |

Actual suite summary: **84 passed, 0 failed, 1 deprecation warning, in 75.76 seconds**. These values are recorded exactly as provided. Warning text/category and the executed command were not provided and cannot be verified from this report. No additional test execution was performed while preparing this document.

## 2. Mapping result to Sprint 1 formal cases

The finalized Sprint 1 catalog contains **38 formal cases**: 28 automated cases linked to existing pytest tests and 10 manual cases. The 84 reported pytest passes are test instances, including parameterized executions and tests spanning the existing backend suite. They are **not 84 formal Sprint 1 cases** and do not mean all 38 formal cases passed.

The 28 automated Sprint 1 cases have existing pytest mappings in `SPRINT1_TEST_CASES.md`. Given the user's report that the existing backend suite completed with 84 passed and 0 failed, the execution status of those mapped pytest tests is recorded as Passed. The mapping and coverage limits remain those documented in the catalog and RTM; a passing underlying test does not expand its assertions or prove complete SRS requirement coverage.

| Sprint 1 case group | Formal case IDs | Cases with mapped pytest tests | Execution status basis |
|---|---|---:|---|
| Authentication | `S1-AUTH-01`–`S1-AUTH-07` | 7 | Existing pytest function mappings; included in reported complete backend suite. |
| Input validation | `S1-INPUT-01`–`S1-INPUT-08` | 8 | Existing pytest function mappings; parameterized tests contribute multiple pytest instances. |
| Role-based access control / privacy | `S1-RBAC-01`–`S1-RBAC-05` | 5 | Existing pytest function mappings; included in reported complete backend suite. |
| Prescription validation and preservation | `S1-PRES-01`–`S1-PRES-07` | 7 | Existing pytest function mappings; includes tests in `test_prescriptions.py`. |
| Backend/database integration | `S1-DB-01` | 1 | Mapped pytest test checks ORM-backed manual prescription and medicine synchronization using the SQLite fixture. |
| **Automated mapped cases** | **28 total** | **28** | **Passed based on user-reported suite result; no separate per-case result file supplied.** |

`S1-DB-01` maps to `test_manual_prescription_has_confirmed_medicine_row` in `backend/tests/test_upload_ocr.py`. This is an automated SQLite ORM relationship check, despite residing in the Sprint 2 test module. It is not a MySQL schema or database integration execution.

The RTM also lists automated test cases that have no direct SRS requirement mapping. Their mapped pytest scenarios are included in the complete-suite result and are recorded Passed in the RTM's unmapped-case inventory. They remain explicitly unmapped to an original SRS ID.

## 3. Manual and MySQL-dependent cases

All 10 manual cases remain **Not Executed** because the reported result is for pytest only:

- `S1-M-AUTH-01`, `S1-M-AUTH-02`
- `S1-M-INPUT-01`, `S1-M-INPUT-02`, `S1-M-INPUT-03`
- `S1-M-PRES-01`
- `S1-M-DB-01`, `S1-M-DB-02`, `S1-M-DB-03`, `S1-M-DB-04`

The four MySQL-dependent manual cases (`S1-M-DB-01` through `S1-M-DB-04`) remain **Not Executed**. The automated suite's SQLite fixture does not provide evidence for MySQL schema constraints, MySQL persistence across sessions, or MySQL write-failure handling.

## 4. Deprecation warning

The user reported one deprecation warning. Its message, source location, and category were not supplied, so this report records the warning count only and does not attribute it to a dependency or code location. The warning is not counted as a test failure. Preserve the full warning output in the execution evidence if it is available.

## 5. Requirement traceability update

`SPRINT1_TEST_CASES.md` and `SPRINT1_RTM.md` record Passed only for automated formal cases with named existing pytest mappings included in the reported complete-suite run. The catalog leaves all manual cases Not Executed. The RTM also records automated project-specific cases without an SRS ID in its unmapped-case inventory. The RTM keeps manual cases Not Executed and retains uncovered/partial requirement assessments; an automated pass does not convert partial coverage into full coverage.

No aggregate status is assigned to a requirement when it has no executed test mapping. Where a requirement maps to both automated and manual cases, the RTM shows the automated result and manual status separately.

## 6. Result limitations and follow-up evidence

- The suite summary is user-supplied; raw pytest output was not included in the repository evidence inspected for this report.
- The exact command, working directory, collection list, and test-to-result output were not supplied. Case-level mapping is based on the existing formal catalog's named pytest mappings and the user's statement that the existing backend suite was executed completely.
- The warning's details are unknown; retain its exact output for triage rather than guessing its cause.
- No MySQL or other manual test result is implied by the pytest run.
- The report does not claim that every SRS requirement is satisfied, that all 38 formal cases passed, or that all tests were run against MySQL.

## 7. Files updated for this execution record

- Created: `documentation/member4/sprint1/SPRINT1_TEST_EXECUTION_REPORT.md`
- Updated: `documentation/member4/sprint1/SPRINT1_TEST_CASES.md`
- Updated: `documentation/member4/sprint1/SPRINT1_RTM.md`
- Application source code and test files were not modified.
