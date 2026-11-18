# Sprint 1 Requirement Traceability Matrix

**Project:** Doctor Prescription to Multilingual Video Reminder and Instruction Generator  
**Baseline:** `documentation/member4/SRS_REQUIREMENTS_BASELINE.md` (source SRS: `TechTitans_SE_SRS-P41_Phase-1.pdf`)  
**Test catalog:** `documentation/member4/sprint1/SPRINT1_TEST_CASES.md`  
**Review reference:** `documentation/member4/sprint1/TEST_CASE_QUALITY_REVIEW.md`  
**Execution status:** 28 mapped automated formal cases are **Passed** based on the user-reported complete pytest suite and named mappings in the catalog. Ten manual cases remain **Not Executed**, including all four MySQL-dependent cases. No MySQL or frontend integration result is implied.

## 1. Scope and conventions

This matrix covers original SRS requirements relevant to Sprint 1 authentication, input validation, authorization/privacy, prescription management, and backend/database integrity. Requirement IDs and descriptions are taken from the SRS baseline. A test case mapping means the case is intended to examine that requirement; it does not mean the requirement is implemented, tested successfully, or fully covered.

- **Automated** means the formal case maps to an existing pytest test. The mapped pytest suite uses FastAPI `TestClient` and an in-memory SQLite database unless the case is explicitly manual/MySQL-dependent.
- **Manual** means the case is planned for later execution outside the current pytest mapping.
- **Direct** means the planned assertions address the requirement’s stated behaviour. **Partial** means the case covers only part of the requirement or a related implementation behaviour.
- `—` means no Sprint 1 case is mapped. Mapped automated status reflects the reported aggregate suite result; manual cases and requirements without executed applicable test cases remain **Not Executed**.
- SRS requirements outside Sprint 1 are listed separately and are not counted as Sprint 1 coverage gaps.

## 2. Functional requirements

| Original SRS ID | Original requirement description | Test Case ID(s) | Testing type | Execution status | Coverage assessment |
|---|---|---|---|---|---|
| REQ-PRES-01 | The system shall allow an authorized Doctor to create a prescription for a registered patient. | S1-PRES-01, S1-PRES-03, S1-INPUT-07, S1-M-DB-02 | Automated; Manual | Automated mapped test(s): Passed (user-reported suite); Manual mapped test(s): Not Executed | Direct for authorized creation and unknown patient handling; S1-M-DB-02 checks persistence. |
| REQ-PRES-02 | The system shall validate mandatory prescription fields before saving. | S1-INPUT-04, S1-INPUT-05, S1-PRES-06, S1-M-INPUT-02, S1-M-DB-01, S1-M-DB-03 | Automated; Manual | Automated mapped test(s): Passed (user-reported suite); Manual mapped test(s): Not Executed | Direct for API required fields and planned DB mandatory-field checks. Update-field case is related validation behaviour. |
| REQ-PRES-03 | The system shall associate each prescription with exactly one patient and one prescribing doctor. | S1-PRES-01, S1-M-DB-01, S1-M-DB-02, S1-M-DB-03 | Automated; Manual | Automated mapped test(s): Passed (user-reported suite); Manual mapped test(s): Not Executed | Partial automated check through returned patient/doctor names; manual MySQL relationship checks are planned. |
| REQ-PRES-04 | The system shall maintain a prescription status such as Pending Verification, Verified, or Rejected. | S1-PRES-01, S1-PRES-04, S1-PRES-05, S1-M-DB-02 | Automated; Manual | Automated mapped test(s): Passed (user-reported suite); Manual mapped test(s): Not Executed | Direct for Pending, Verified, and Rejected API status behaviour; manual case checks persistence. |

## 3. Security and authentication requirements

| Original SRS ID | Original requirement description | Test Case ID(s) | Testing type | Execution status | Coverage assessment |
|---|---|---|---|---|---|
| NFR-SEC-01 | The system shall require authentication before allowing users to access protected functionality. | S1-AUTH-01, S1-AUTH-02, S1-AUTH-04, S1-RBAC-02, S1-M-AUTH-01, S1-M-AUTH-02 | Automated; Manual | Automated mapped test(s): Passed (user-reported suite); Manual mapped test(s): Not Executed | Direct for authentication gate and login/token behaviour; expired/tampered token checks are manual only. |
| NFR-SEC-02 | The system shall implement role-based access control for Doctor, Patient, and Administrator users. | S1-RBAC-01, S1-RBAC-02, S1-RBAC-04, S1-PRES-03 | Automated | Passed (mapped pytest tests; user-reported suite) | Direct for selected role restrictions; no requirement-wide role/function matrix is covered. |
| NFR-SEC-03 | The system shall restrict doctors to authorized patient and prescription records. | S1-RBAC-03, S1-RBAC-04 | Automated | Passed (mapped pytest tests; user-reported suite) | Direct for tested patient-profile and prescription ownership cases. |
| NFR-SEC-04 | Patients shall only be permitted to access their own prescription, generated instructions, and reminder information. | S1-RBAC-04 | Automated | Passed (mapped pytest tests; user-reported suite) | Partial: prescription privacy is covered; generated instructions and reminders are not part of Sprint 1 backend scope. |
| NFR-SEC-05 | User passwords shall not be stored in plain text. | S1-AUTH-03 | Automated | Passed (mapped pytest tests; user-reported suite) | Direct for password hashing and omission of password fields from registration response. |
| NFR-SEC-06 | The deployed system shall use HTTPS for communication between the client and server. | — | — | Not Executed | No deployment/HTTPS test case in Sprint 1 catalog. |
| NFR-SEC-07 | The system shall validate and sanitize user inputs to reduce security risks caused by malicious or invalid input. | S1-INPUT-02, S1-INPUT-05, S1-INPUT-08, S1-M-INPUT-01, S1-M-INPUT-02 | Automated; Manual | Automated mapped test(s): Passed (user-reported suite); Manual mapped test(s): Not Executed | Partial: listed format, blank, and boundary inputs are addressed; broad malicious-input/security validation is not. |
| NFR-SEC-08 | The system shall prevent unauthorized users from accessing prescription records through manipulated requests. | S1-RBAC-03, S1-RBAC-04 | Automated | Passed (mapped pytest tests; user-reported suite) | Direct for tested cross-patient/doctor ID access and ownership checks. |
| NFR-SEC-09 | The system shall implement session management to prevent unauthorized access through expired or inactive sessions. | S1-M-AUTH-02 | Manual | Not Executed | Partial planned coverage for expired tokens; inactive-session handling is not specified by the current JWT API and is not separately covered. |
| NFR-SEC-10 | The system shall maintain audit records for important operations such as prescription creation, modification, and deletion. | — | — | Not Executed | No audit-log test case is present. |
| NFR-SEC-11 | Sensitive patient and prescription information shall be protected against unauthorized access during storage and transmission. | — | — | Not Executed | No encryption-at-rest or transport-protection test case is present. Password hashing coverage alone does not cover this requirement. |
| NFR-SEC-12 | Access to administrative functions shall be restricted to authenticated administrators. | S1-RBAC-02 | Automated | Passed (mapped pytest tests; user-reported suite) | Direct for selected admin endpoints and role denials. |

## 4. Safety requirements

| Original SRS ID | Original requirement description | Test Case ID(s) | Testing type | Execution status | Coverage assessment |
|---|---|---|---|---|---|
| NFR-SAFE-01 | The system shall not independently prescribe medicines or recommend changes to a doctor's prescription. | — | — | Not Executed | No test case examines generated advice/diagnosis; instruction-generation functionality is outside Sprint 1. |
| NFR-SAFE-02 | The system shall preserve the medicine name, dosage, frequency, and duration specified in the doctor's prescription. | S1-PRES-02, S1-DB-01, S1-M-PRES-01 | Automated; Manual | Automated mapped test(s): Passed (user-reported suite); Manual mapped test(s): Not Executed | Partial: exact dosage preservation is tested; the full medicine/frequency/duration set is not compared end to end. |
| NFR-SAFE-03 | The system shall identify and report missing or invalid mandatory prescription information before processing. | S1-INPUT-04, S1-INPUT-05, S1-M-INPUT-02 | Automated; Manual | Automated mapped test(s): Passed (user-reported suite); Manual mapped test(s): Not Executed | Direct for required/missing/blank API fields and planned schema-boundary checks; OCR processing is outside Sprint 1. |
| NFR-SAFE-04 | The system shall require verification of prescription information before generating final medication instructions. | — | — | Not Executed | S1-PRES-04 tests prescription verification status but no final instruction-generation gate exists in the Sprint 1 cases. No direct coverage. |
| NFR-SAFE-05 | The system shall clearly indicate that generated instructions are based on the provided prescription and are not a substitute for professional medical advice. | — | — | Not Executed | No generated instructions or disclaimer test in Sprint 1 scope. |
| NFR-SAFE-06 | The system shall not silently modify medication names, dosage, frequency, or duration during processing or translation. | S1-PRES-02, S1-PRES-06, S1-M-PRES-01 | Automated; Manual | Automated mapped test(s): Passed (user-reported suite); Manual mapped test(s): Not Executed | Partial: dosage preservation/blanking is covered; other medication fields and translation are not covered end to end. |
| NFR-SAFE-07 | If the system detects incomplete or ambiguous prescription information, it shall request verification instead of generating potentially incorrect instructions. | — | — | Not Executed | No ambiguity/instruction-generation gate test in Sprint 1. |
| NFR-SAFE-08 | The system shall allow an authorized user to correct prescription information before generating the final video reminder. | S1-PRES-04 | Automated | Passed (mapped pytest tests; user-reported suite) | Partial: pre-verification prescription update is covered; final video generation is not part of Sprint 1. |
| NFR-SAFE-09 | The system shall display appropriate error messages when prescription processing fails. | — | — | Not Executed | OCR/prescription processing failures are Sprint 2 scope; no Sprint 1 case covers this. |
| NFR-SAFE-10 | The system shall not generate a medication reminder when required prescription or scheduling information is invalid. | — | — | Not Executed | Reminder generation/scheduling is outside Sprint 1. |

## 5. Relevant performance and software quality requirements

| Original SRS ID | Original requirement description | Test Case ID(s) | Testing type | Execution status | Coverage assessment |
|---|---|---|---|---|---|
| NFR-PERF-02 | The system shall save a valid prescription within 2 seconds after submission, excluding delays caused by external services. | — | — | Not Executed | No timing measurement or performance test case is present. |
| NFR-QUAL-02 | The system shall provide clear and meaningful error messages for invalid or incomplete inputs. | S1-INPUT-01 through S1-INPUT-08; S1-M-INPUT-01 through S1-M-INPUT-03 | Automated; Manual | Automated mapped test(s): Passed (user-reported suite); Manual mapped test(s): Not Executed | Partial: several cases assert validation status; none assesses clarity/meaningfulness of message text. |
| NFR-QUAL-05 | The system shall preserve successfully stored prescription information during normal application failures. | S1-M-DB-02, S1-M-DB-04 | Manual | Not Executed | Partial: planned persistence across sessions and preservation of a baseline record during simulated DB failure; neither is executed. |
| NFR-QUAL-07 | The system shall display an appropriate failure message when an operation is unsuccessful instead of displaying a false success message. | S1-M-DB-04 | Manual | Not Executed | Planned only for database persistence failure; broader operation failures are not covered. |
| NFR-QUAL-11 | Major system modules shall have testable interfaces for unit and integration testing. | S1-AUTH-01 through S1-DB-01 | Automated | Passed (mapped pytest tests; user-reported suite) | Partial/indirect: current API modules have pytest-facing interfaces; this does not assess all major modules or standalone unit-test interfaces. |
| NFR-QUAL-12 | Functional and nonfunctional requirements shall be mapped to corresponding test cases through the Requirement Traceability Matrix. | — (this RTM is the traceability artifact) | — | Not Executed | This artifact maps Sprint 1 scope only; it does not complete project-wide traceability for Sprint 2/future requirements. No execution test case. |

## 6. Database, privacy, and legal/domain requirements

| Original SRS ID | Original requirement description | Test Case ID(s) | Testing type | Execution status | Coverage assessment |
|---|---|---|---|---|---|
| OR-DB-01 | The system shall maintain a unique identifier for each registered user. | S1-M-DB-01, S1-M-DB-02 | Manual | Not Executed | Partial: schema inspection and persistence are planned; no duplicate-ID behaviour test is executed. |
| OR-DB-02 | Each prescription shall have a unique prescription identifier. | S1-M-DB-01, S1-M-DB-02 | Manual | Not Executed | Partial: schema primary-key inspection and persistence are planned; no duplicate-ID operation is executed. |
| OR-DB-03 | Each prescription shall be associated with the corresponding patient and authorized doctor. | S1-PRES-01, S1-M-DB-01, S1-M-DB-02, S1-M-DB-03 | Automated; Manual | Automated mapped test(s): Passed (user-reported suite); Manual mapped test(s): Not Executed | Partial automated name/association assertions; direct MySQL FK/association checks are planned. |
| OR-DB-05 | The database shall maintain appropriate relationships between users, patients, prescriptions, medicines, reminders, and generated videos. | S1-DB-01 | Automated | Passed (mapped pytest tests; user-reported suite) | Partial: current SQLite ORM test checks only prescription-to-medicine relation; other listed entities are not tested here. |
| OR-DB-06 | The system shall validate mandatory database fields before storing records. | S1-M-DB-01, S1-M-DB-03 | Manual | Not Executed | Planned MySQL schema and direct invalid-insert checks. |
| OR-DB-07 | The system shall prevent unauthorized modification or deletion of stored prescription information. | S1-RBAC-04 | Automated | Passed (mapped pytest tests; user-reported suite) | Partial: API-level unauthorized update is covered; database-level enforcement and prescription deletion are not tested. |
| OR-PRIV-02 | Patient and prescription information shall not be displayed to unauthorized users. | S1-RBAC-03, S1-RBAC-04 | Automated | Passed (mapped pytest tests; user-reported suite) | Direct for tested cross-patient profile/prescription requests; generated media is outside Sprint 1. |
| OR-PRIV-03 | The system shall implement access controls for stored patient information. | S1-RBAC-01, S1-RBAC-03 | Automated | Passed (mapped pytest tests; user-reported suite) | Direct for own-profile and doctor/patient profile access scenarios. |
| BR-01 | Only an authenticated and authorized doctor shall be permitted to create or modify a patient's prescription. | S1-PRES-01, S1-PRES-03, S1-RBAC-04 | Automated | Passed (mapped pytest tests; user-reported suite) | Direct for authorized creation and selected unauthorized create/update attempts. |
| BR-02 | A patient shall only be permitted to view their own prescription and reminder information. | S1-RBAC-03, S1-RBAC-04 | Automated | Passed (mapped pytest tests; user-reported suite) | Direct for prescription/profile ownership; reminder information is outside Sprint 1. |
| BR-03 | The system shall use the medication information supplied in the doctor's prescription as the source for generating instructions. | S1-PRES-02, S1-M-PRES-01 | Automated; Manual | Automated mapped test(s): Passed (user-reported suite); Manual mapped test(s): Not Executed | Partial: stored dosage preservation is covered; instruction generation/source use is not tested. |
| BR-04 | The system shall not automatically modify a doctor's prescribed dosage. | S1-PRES-02, S1-M-PRES-01 | Automated; Manual | Automated mapped test(s): Passed (user-reported suite); Manual mapped test(s): Not Executed | Direct for dosage storage characterization; no downstream processing/translation comparison. |
| BR-11 | The system shall treat the doctor's prescription as the authoritative source of medication information. | S1-PRES-02, S1-M-PRES-01 | Automated; Manual | Automated mapped test(s): Passed (user-reported suite); Manual mapped test(s): Not Executed | Partial: dosage preservation only; no instruction-generation source trace. |
| OR-LEGAL-02 | The system shall preserve the original prescription information provided by an authorized user. | S1-PRES-02 | Automated | Passed (mapped pytest tests; user-reported suite) | Partial: exact dosage text is checked; all original prescription fields are not compared. |

## 7. Requirements with no Sprint 1 test coverage

The following in-scope requirements have no direct mapped test case in the Sprint 1 catalog. They remain **Not Executed**. Some related behaviours are tested, but those do not satisfy the complete requirement.

| Original SRS ID | Requirement area | Coverage gap |
|---|---|---|
| NFR-PERF-02 | Prescription save performance | No ≤2-second timing case. |
| NFR-SEC-06 | HTTPS in deployment | No transport/deployment test. |
| NFR-SEC-10 | Audit records | No audit-event assertions. |
| NFR-SEC-11 | Sensitive data protection at rest and in transit | No storage/transport protection assessment. |
| NFR-SAFE-01 | No independent prescribing/recommendations | No generated-output safety test. |
| NFR-SAFE-04 | Verification before final medication instructions | Prescription status is tested, but no final-instruction generation gate is tested. |
| NFR-SAFE-05 | Professional-medical-advice disclaimer | No generated instruction UI/content test. |
| NFR-SAFE-07 | Ambiguous/incomplete data requests verification before instructions | No instruction-generation ambiguity gate test. |
| NFR-SAFE-09 | Processing-failure error message | No Sprint 1 processing/OCR failure case. |
| NFR-SAFE-10 | Invalid data blocks medication reminders | Reminder generation is outside Sprint 1. |
| NFR-QUAL-02 | Clear, meaningful validation errors | Status codes are checked; error-message clarity is not. |
| NFR-QUAL-11 | Testable interfaces across major modules | Existing API tests provide indirect evidence only; not all module interfaces are assessed. |
| NFR-QUAL-12 | RTM traceability | This document maps Sprint 1 only; project-wide RTM coverage is incomplete. |

Partial coverage is identified in the main matrix for `NFR-SAFE-02`, `NFR-SAFE-06`, `NFR-SAFE-08`, `NFR-QUAL-05`, `NFR-QUAL-07`, `OR-DB-01`–`OR-DB-03`, `OR-DB-05`–`OR-DB-07`, `BR-03`, `BR-11`, and `OR-LEGAL-02`.

## 8. Test cases not mapped to an original SRS requirement ID

These cases address implemented project behaviour or validation expectations for which the SRS baseline contains no directly applicable requirement ID. They remain in the RTM for test inventory and project traceability; no IDs are invented.

| Test Case ID | Scenario | Type | Reason no direct SRS requirement ID applies | Execution status |
|---|---|---|---|---|
| S1-AUTH-05 | Duplicate email registration | Automated | Registration uniqueness rule is implemented but not specified as an SRS functional requirement. | Passed (mapped pytest test; user-reported suite) |
| S1-AUTH-06 | Case-insensitive email registration/login | Automated | Email normalization behaviour is not specified by an SRS requirement. | Passed (mapped pytest test; user-reported suite) |
| S1-AUTH-07 | Admin self-registration rejection | Automated | The SRS defines an Administrator actor but does not specify this registration flow. | Passed (mapped pytest test; user-reported suite) |
| S1-INPUT-01 | Missing Patient registration fields | Automated | Registration required fields have no SRS functional requirement ID. | Passed (mapped pytest test; user-reported suite) |
| S1-INPUT-03 | Doctor specialization and duplicate-license registration validation | Automated | These registration rules are implementation/project responsibilities, not specified SRS FRs. | Passed (mapped pytest test; user-reported suite) |
| S1-INPUT-06 | Future prescription date rejection | Automated | The SRS does not define a future-date rule. | Passed (mapped pytest test; user-reported suite) |
| S1-RBAC-05 | Unknown patient profile lookup returns 404 | Automated | The SRS does not define this endpoint or its response code. | Passed (mapped pytest test; user-reported suite) |
| S1-PRES-07 | Unknown prescription detail returns 404 | Automated | The SRS does not define the endpoint response code. | Passed (mapped pytest test; user-reported suite) |
| S1-M-INPUT-03 | Whitespace-only Patient/Doctor registration names | Manual | Registration name validation is not specified by an SRS functional requirement. | Not Executed |

Cases with both a project-specific scenario and an applicable SRS security/validation requirement remain mapped in the main matrix and are not repeated here.

## 9. Sprint 1 exclusions

The following requirement groups are not mapped as Sprint 1 gaps because they belong to later or wider project scope: `REQ-PROC-01`–`REQ-PROC-04` (upload/OCR processing), `REQ-TRANS-01`–`REQ-TRANS-03`, `REQ-VID-01`–`REQ-VID-03`, `REQ-REM-01`–`REQ-REM-04`, reminder-specific `BR-05`–`BR-10`, `OR-DB-04` (reminder relationships), and `OR-DB-08` (deployment backup/recovery). Translation, videos, reminders, medication tracking, and pharmacy integration are not part of this Sprint 1 case catalog. Other system-wide requirements not directly related to Sprint 1 auth/prescription/database testing (for example UI, accessibility, deployment portability, and external-service requirements) remain for their appropriate sprint/system test plans.

## 10. Execution status update and consistency validation

Execution evidence supplied by the user: the existing backend pytest suite was run under Python 3.11.18 with pytest 8.3.4 and reported **84 passed, 0 failed, 1 deprecation warning, in 77.13 seconds**. The execution date, command line, warning text, and per-test output were not supplied. This RTM update relies on that suite summary plus the existing catalog-to-pytest mappings; it does not assert that 84 formal Sprint 1 cases passed.

| Validation item | Result |
|---|---:|
| Formal test cases in the Sprint 1 catalog | 38 |
| Automated formal cases with existing pytest mappings | 28; mapped tests are reported passed in the suite summary |
| Manual formal cases | 10; Not Executed |
| MySQL-dependent manual cases | 4 (`S1-M-DB-01`–`S1-M-DB-04`); Not Executed |
| Pytest test instances reported passed | 84 (not equivalent to formal test case count) |
| Pytest failures reported | 0 |
| Deprecation warnings reported | 1; details not supplied |
| Execution time reported | 77.13 seconds |
| Automated formal cases marked Passed based on mapped suite tests | 28 of 28 |
| Manual formal cases marked Passed | 0 of 10 |
| All 38 formal cases passed as a blanket claim | No |

The 28 automated formal cases in Sections 2–6 and the automated cases without an SRS mapping in Section 8 show Passed only where the finalized catalog names a pytest mapping included in the user-reported complete-suite run. Individual pytest output was not supplied, so the pass status is trace-mapped from aggregate evidence, not from a per-case result artifact. This is test-execution status only; partial coverage assessments remain partial, and passing tests do not establish full requirement satisfaction. All manual cases remain Not Executed. SRS requirements without an applicable mapped test case remain uncovered/Not Executed. The 84 pytest test instances include parameterized executions and tests across the existing backend suite, so the number must not be reported as 84 formal Sprint 1 cases or as all 38 formal cases passing.

MySQL-dependent cases use explicit schema expectations: `S1-M-DB-01` and `S1-M-DB-03` use Sprint 1 scripts 01–05 for SQL-only checks; `S1-M-DB-02` and `S1-M-DB-04` require scripts 01–08 or an equivalent schema compatible with the current backend models. Existing automated API tests use SQLite, not MySQL.
