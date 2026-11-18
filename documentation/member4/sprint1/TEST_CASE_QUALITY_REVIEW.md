# Sprint 1 Test Case Quality Review

**Reviewed document:** `documentation/member4/sprint1/SPRINT1_TEST_CASES.md`  
**Review basis:** SRS requirements baseline, source SRS, backend routes/schemas/security/models, existing Sprint 1 pytest modules, and Sprint 1 database schema.  
**Original review execution:** No tests were run during the initial static review. The detailed findings below preserve that review of the then-current 32-case draft. See Section 9 for the follow-up review of the finalized 38-case catalog and the user-reported execution summary.

## 1. Historical review: 32-case draft

The following review sections (1–8) preserve findings for the earlier draft, which had **32 uniquely identified test cases**: 23 in the existing automated pytest mapping section and 9 identified as manual. All 32 rows include the requested fields, all Actual Result cells are blank, all statuses are `Not Executed`, priorities use High/Medium, and test types use API, Security, Integration, or Manual. No nonexistent application endpoint was found in the test steps.

The document is useful as a test draft, but several cases need clarification before execution. Main issues:

- Some expected results claim no data was created or existing data stayed unchanged, while the mapped pytest only asserts a response status.
- Several SRS mappings are broader than the mapped test scenario supports.
- The manual MySQL cases that call the current backend specify only Sprint 1 schema, which is incompatible with the current ORM/API model unless the later schema updates are also applied.
- The empty/whitespace registration case has a statically identifiable implementation mismatch: a two-space Patient/Doctor name passes the initial minimum-length check, is cleaned to an empty string, and is not revalidated.
- A few unrepresented registration scenarios already have pytest coverage, while some manual scenarios overlap existing tests.

These are review findings, not test execution results.

## 2. Required-field and structure audit

| Check | Result | Notes |
|---|---|---|
| All required test case fields present | **Pass** | Every case row includes ID, scenario, SRS ID/applicability, preconditions, input, steps, expected result, actual result, status, priority, and type. Automated rows also include an existing pytest mapping column. |
| Unique test case IDs | **Pass** | 32 rows, 32 unique IDs. |
| Actual result fields blank | **Pass** | All 32 Actual Result cells are blank. |
| Status field | **Pass** | All 32 are `Not Executed`. |
| Priority/type values | **Pass** | Priorities are High/Medium. Types are API, Security, Integration, or Manual. No isolated Unit case is claimed. |
| Existing tests distinguished from manual cases | **Pass with caveat** | The sections distinguish them, but the “manual cases” section includes partial overlap with existing automated scenarios; see findings. |
| No test execution | **Pass** | No test command was run for this review. |

## 3. Case-by-case mapping review

“Good” means the named test genuinely exercises the central scenario stated. “Partial” means it exercises part of the expected result or its mapping/scope needs adjustment. These labels do not indicate a pass/fail outcome from test execution.

| Test Case ID | Review | Mapping / expected-result finding |
|---|---|---|
| S1-AUTH-01 | Good | `test_login_success_returns_token_and_role` covers Patient login, HTTP 200, token and role. No Doctor login case is included; see coverage gaps. |
| S1-AUTH-02 | Good | `test_login_failures_are_indistinguishable` submits wrong password and unknown email and compares 401 responses. |
| S1-AUTH-03 | Good | `test_password_is_hashed_in_db` checks persisted bcrypt-style hash; `test_register_patient_and_doctor` checks the response omits password fields. It does not separately test `verify_password` in isolation, but the successful login case exercises password verification through the API. |
| S1-AUTH-04 | Partial | `test_me_requires_valid_token` checks missing token, garbage token, and valid token on `/auth/me`; `test_endpoints_require_authentication` checks missing token on several routes. `NFR-SEC-09` is not tested here because expiry is not part of this case’s input/steps. Keep `NFR-SEC-09` on S1-M-AUTH-02 only, or add an expired-token scenario to this case. |
| S1-INPUT-01 | Partial | `test_missing_patient_fields` parameterizes all six omitted Patient fields and expects 422. The test does not query the database to prove no account was created, so narrow that clause or add a persistence assertion. |
| S1-INPUT-02 | Partial | `test_invalid_patient_inputs` covers the listed password, email, phone, name, and DOB examples. It asserts 422, not absence of a persisted account; adjust the expected result or add a persistence check. |
| S1-INPUT-03 | Partial | `test_doctor_requires_specialization` and `test_duplicate_license_rejected` cover the two rejection responses. The duplicate-license test does not assert the second account is absent from the database. Registration rules have no explicit SRS FR ID, which the document correctly states. |
| S1-INPUT-04 | Partial | `test_mandatory_fields_required` covers all six omitted prescription fields with 422. It does not assert database row count/persistence, so “no incomplete prescription is created” is not directly asserted by the mapped test. |
| S1-INPUT-05 | Good / minor assertion gap | `test_blank_fields_rejected` checks whitespace-only text for all four required medicine fields and expects 422. It does not explicitly query persistence; because validation precedes route handling, the main rejection assertion is still a direct match. |
| S1-INPUT-06 | Partial | `test_future_date_and_unknown_patient_rejected` checks 422 and 404 respectively. It does not verify no prescription row was created. `REQ-PRES-02` is not directly exercised by this case (no missing mandatory fields); remove it from this mapping. `REQ-PRES-01` is relevant to requiring a registered patient. |
| S1-INPUT-07 | Partial | `test_patient_update_validation` checks invalid phone/null/future DOB responses. It does not inspect the profile afterward, so “profile retains valid prior values” is not covered. `NFR-SEC-04` concerns patient access to prescriptions/instructions/reminders, not profile input validation; remove it from this mapping. |
| S1-RBAC-01 | Good | `test_patient_profile_get_and_update` checks the patient’s own profile and a successful update. The applicable privacy/data-access intent is `OR-PRIV-03`; the case is a sensible role test. |
| S1-RBAC-02 | Good | The four named pytest functions cover Patient/Doctor denials and Admin access to `/admin/users` and `/admin/stats`. The endpoint paths exist in the source. |
| S1-RBAC-03 | Good, criterion is implementation-specific | The two named tests cover cross-patient denial and Doctor access after an associated prescription, including denial for another Doctor. The SRS says doctors are restricted to authorized records but does not define “authorized” as “after prescribing”; mark that access rule as an implementation-derived criterion rather than an exact SRS rule. |
| S1-RBAC-04 | Partial | The three mapped tests cover Patient verified-own visibility, Doctor ownership, and Admin prescription read/verify restrictions. The SRS does not specify that Admin may view every prescription; keep that as observed implementation behaviour, not an SRS acceptance criterion. `NFR-SEC-12` covers access to administrative functions, not Admin prescription visibility. |
| S1-PRES-01 | Partial | `test_doctor_creates_prescription_as_pending` asserts creation status, verification/processing/status values, and patient/doctor names. It does not assert all submitted medication fields, patient ID, or doctor ID. Also remove `REQ-PRES-02` from this valid-data case: mandatory-field rejection is tested in S1-INPUT-04. `REQ-PRES-01`, `REQ-PRES-03`, and `REQ-PRES-04` are appropriate. |
| S1-PRES-02 | Good | `test_dosage_text_preserved_exactly` creates with `250 mg/5 ml`, retrieves the prescription, and compares exact dosage text. |
| S1-PRES-03 | Partial | `test_patient_and_admin_cannot_create` checks both 403 responses. It does not assert the prescription count remains unchanged. `REQ-PRES-01`, `BR-01`, and general role control `NFR-SEC-02` are the strongest mappings. `NFR-SEC-03` is Doctor record scoping; `NFR-SEC-12` is administrative function access and neither directly specifies non-Doctor prescription creation denial. |
| S1-PRES-04 | Good for implementation behaviour; SRS scope needs a label | `test_update_then_verify_then_locked` covers update, verification, post-verification content lock, and status update. The lock after verification is implemented, but the SRS does not explicitly require this lock. Keep it labelled as project/implementation behaviour; `REQ-PRES-04` and safety verification requirements support the lifecycle portions. |
| S1-PRES-05 | Good | `test_reject` checks verification and processing statuses become Rejected; `REQ-PRES-04` is an appropriate mapping. |
| S1-PRES-06 | Partial | `test_update_cannot_blank_required_field` checks null and empty dosage updates return 422. It does not GET the record afterward to assert the old dosage remains unchanged. |
| S1-PRES-07 | Good | `test_missing_prescription_404` checks the specified existing detail endpoint for a nonexistent ID. The document correctly avoids claiming an SRS response-code requirement. |
| S1-DB-01 | Good with environment caveat | `test_manual_prescription_has_confirmed_medicine_row` creates a manual prescription and verifies a related confirmed Medicine row plus header/row synchronization. It runs against the SQLite ORM fixture, not MySQL; the document discloses this. The test does not validate MySQL schema initialization. |
| S1-M-AUTH-01 | Good manual case | `/auth/login` exists; `LoginRequest` uses `EmailStr` and a non-empty password field, so malformed/missing/empty requests are expected to fail request validation. This is correctly identified as a project testing responsibility. |
| S1-M-AUTH-02 | Good manual case; setup could be clearer | The auth dependency decodes JWTs and maps JWT errors to 401, so expired/tampered/malformed tokens are valid negative cases. Specify generating a deliberately expired token in a controlled test setup rather than waiting for the default 60-minute token to expire. |
| S1-M-INPUT-01 | Partial; includes a duplicate dimension and a likely code defect | Omitted required Patient fields are already covered by S1-INPUT-01 and Doctor specialization by S1-INPUT-03; scope this manual case to empty/whitespace values. Static code inspection shows a two-space `name` passes the pre-clean minimum length, is normalized to `""`, and is not revalidated by `RegisterRequest`; the expected rejection may fail for that value. Other empty required fields are checked by the role validator/field validators. |
| S1-M-INPUT-02 | Manual classification is correct; case needs a more exact matrix | Wrong types and boundary testing are absent as a complete suite, so Manual is appropriate. The data field lists ranges, but does not enumerate each below/at/above boundary and valid paired inputs. Define exact boundary values per field to make repeatable execution and expected outcomes unambiguous. |
| S1-M-PRES-01 | Good characterization case | Current medicine schema accepts required dosage as nonblank text up to 100 characters and contains no dosage grammar/range. The case correctly avoids inventing a medical rule. The >100-character value has an objective rejection expectation; arbitrary nonblank values should remain recorded as characterization pending a product rule. |
| S1-M-DB-01 | Good MySQL manual case | The Sprint 1 SQL scripts create database, roles/users, patients, doctors, and prescriptions with the described constraints. The case correctly notes that no pytest test validates them. |
| S1-M-DB-02 | Needs correction before execution | Current SQLAlchemy `Prescription` model includes `processing_status`, and model/API outputs include Sprint 2 relationships (`medicines`, `files`). Sprint 1 SQL files 01–05 do not define `processing_status`, `medicines`, or `prescription_files`; the backend cannot be expected to run against only that schema. Use a MySQL schema brought to the current model level (scripts 01–08) while limiting assertions to Sprint 1 behaviours, or isolate SQL-only Sprint 1 checks. |
| S1-M-DB-03 | Partial; split scope and fix precondition | Direct MySQL constraint checks are appropriate, but the API unauthorized-update subscenario overlaps S1-PRES-03/S1-RBAC-04 and should be removed or explicitly treated as already covered. The same Sprint 1-only schema incompatibility applies to backend API calls. Direct SQL constraint checks and application authorization are distinct layers. |
| S1-M-DB-04 | Partial; incorrect SRS mapping and same schema issue | `OR-DB-06` is mandatory database-field validation, not database-unavailable/write-failure handling. `NFR-QUAL-07` is directly relevant to reporting failure rather than false success. `NFR-QUAL-05` concerns preserving successfully stored data through normal application failures and is only relevant if the case explicitly verifies prior data remains intact. Backend invocation also needs schema compatible with current models. |

## 4. Incorrect or overbroad SRS mappings

| Case | Mapping issue | Review recommendation |
|---|---|---|
| S1-AUTH-04 | `NFR-SEC-09` is mapped, but automated case steps cover missing/garbage/valid tokens, not expired/inactive sessions. | Move `NFR-SEC-09` to S1-M-AUTH-02 or add an expiry scenario to the automated case later. |
| S1-INPUT-06 | `REQ-PRES-02` concerns mandatory fields; the mapped test covers a future date and unknown patient. | Remove `REQ-PRES-02`; retain `REQ-PRES-01` for the registered-patient constraint and `NFR-SEC-07` for input validation as applicable. |
| S1-INPUT-07 | `NFR-SEC-04` concerns patient access to prescriptions, instructions, and reminders; this case is profile input validation. | Remove `NFR-SEC-04`; retain `NFR-SEC-07` for input validation. |
| S1-RBAC-04 | `NFR-SEC-12` concerns access to administrative functions, not an Admin’s permission to read prescription records. Admin prescription visibility is not explicitly defined in the SRS. | Mark Admin prescription viewing as implementation behaviour; do not present it as an SRS acceptance criterion. |
| S1-PRES-01 | The range `REQ-PRES-01`–`REQ-PRES-04` includes `REQ-PRES-02` field validation, which this valid prescription case does not challenge. | Remove `REQ-PRES-02`; field-validation coverage belongs to S1-INPUT-04/05. |
| S1-PRES-03 | `NFR-SEC-03` addresses Doctor scope; `NFR-SEC-12` addresses administrative functions. Neither expressly states that Patient/Admin cannot create prescriptions. | Use `REQ-PRES-01`, `BR-01`, and general `NFR-SEC-02` as the relevant basis; keep exact role denial as the implementation check. |
| S1-M-DB-04 | `OR-DB-06` is mapped to persistence failure handling but only requires mandatory database-field validation. | Remove `OR-DB-06`; retain `NFR-QUAL-07`, and retain `NFR-QUAL-05` only if preservation of prior successful data is explicitly checked. |

Other mappings are broadly consistent with the baseline. Registration/login cases appropriately avoid invented functional IDs. `REQ-PRES-04` supports pending/verified/rejected status cases; it does not itself specify post-verification locking.

## 5. Duplicate and overlap review

No duplicate test case IDs or exact duplicate formal cases were found. The following overlaps should be narrowed:

- **S1-M-INPUT-01** repeats omitted required registration-field scenarios from S1-INPUT-01 and S1-INPUT-03. Keep it focused on empty/whitespace values.
- **S1-M-DB-03** includes unauthorized API modification already represented in S1-PRES-03 and S1-RBAC-04. Keep the database case focused on direct SQL constraints, or separately reference the existing API cases without rerunning them as a new manual scenario.
- **S1-AUTH-04** maps `test_me_requires_valid_token` and `test_endpoints_require_authentication`; those cover overlapping unauthenticated access but on different paths. This is not a duplicate formal case, but the case description should explicitly list the paths covered if that breadth is intended.

## 6. Endpoint and implementation consistency

All API paths named in the cases exist in the current FastAPI routers: `/auth/register`, `/auth/login`, `/auth/me`, `/patients/me`, `/patients`, `/patients/{patient_id}`, `/admin/users`, `/admin/stats`, `/prescriptions`, and `/prescriptions/{prescription_id}` with the described GET/PUT/POST methods. No nonexistent upload, OCR, translation, reminder, or frontend route was introduced into Sprint 1 cases.

Important test setup distinction: the pytest fixture sets `DATABASE_URL=sqlite://`, creates all tables from ORM metadata, and overrides the application DB dependency. It does not run `database/schema/*.sql` or connect to MySQL. Also, the current ORM contains Sprint 2 fields and entities that are absent from the Sprint 1-only SQL state. The test document notes SQLite-vs-MySQL differences, but the preconditions of S1-M-DB-02/03/04 should explicitly resolve the schema version mismatch.

## 7. Coverage gaps and traceability omissions

### Existing pytest cases not mapped to a formal test case

The following Sprint 1 pytest scenarios exist but have no dedicated formal row or explicit mapping in the document:

- `test_duplicate_email_rejected`
- `test_email_is_case_insensitive`
- `test_admin_cannot_self_register`
- `test_unknown_patient_404` in `test_patients_rbac.py` (separate from unknown patient on prescription creation)

These are existing automated coverage, not missing implementation tests. Add formal IDs or explicitly map them under an appropriate existing case if their outcomes are included.

### Scenarios without current automated coverage

- Doctor successful login specifically; existing login success uses a Patient account.
- Login missing/malformed requests and empty password (included as a manual case).
- Expired/tampered/wrong-signature token cases (included as manual case).
- Whitespace-only registration name (included as manual case; static implementation indicates two spaces can pass).
- Broad invalid-type and boundary matrix (included as manual case but needs concrete values).
- Actual MySQL schema execution, MySQL persistence across sessions, and direct MySQL foreign-key/unique/NOT NULL enforcement (manual cases).
- Persistence-state assertions after rejected creates/updates are absent from several mapped pytest functions, even where the formal expected result currently says no data changed.
- Rollback/atomicity behaviour for database write failures has no existing pytest mapping.

### SRS requirements that are out of Sprint 1 case scope

The test document correctly excludes Sprint 2 upload/OCR and future translation, video, reminder, medication tracking, and pharmacy integration cases. Do not treat absence of those cases as a Sprint 1 omission. Registration/login workflows have no dedicated SRS functional requirement IDs, as documented.

## 8. Recommended document corrections

1. Tighten mappings listed in Section 4 and distinguish SRS acceptance criteria from implementation-specific expectations, especially Admin prescription visibility and verified-prescription locking.
2. Narrow S1-M-INPUT-01 to empty/whitespace cases and record the `name` normalization issue as an expected implementation defect candidate.
3. Make the MySQL schema preconditions of S1-M-DB-02/03/04 consistent with the current backend model version; separate direct SQL tests from API authorization cases.
4. Narrow expected results where the mapped pytest asserts only a status code, or add persistence assertions in a future test implementation.
5. Add traceability rows for the existing duplicate-email, case-insensitive-email, Admin self-registration, and patient unknown-ID pytest cases, or explicitly cross-reference them.
6. Specify an exact boundary-value matrix for S1-M-INPUT-02 and a deterministic way to create an expired JWT for S1-M-AUTH-02.

At the time of the original review, no changes were made to the test-case document, application source, tests, or SQL files.


## 9. Follow-up review: finalized 38-case catalog and execution record

This follow-up supersedes the historical counts and “no execution” statements above. The finalized catalog now contains **38 unique cases: 28 automated and 10 manual**. This review was static; tests were not rerun. The execution figures below are user-reported and cross-referenced to the named pytest mappings in the finalized catalog.

| Check | Current result | Notes |
|---|---|---|
| Formal case IDs | **Pass** | 38 unique IDs; 28 automated and 10 manual. The RTM contains all 38 IDs, with no missing or unexpected case IDs. |
| Required fields | **Pass** | All case rows retain the requested fields. The automated cases now have aggregate-result notes and Passed status; manual Actual Result cells remain blank and statuses remain Not Executed. |
| Automated mapping and status | **Passed (aggregate evidence)** | Each of the 28 automated rows names at least one existing pytest test. User reported the complete backend suite as 84 passed, 0 failed. The raw output and per-test report were not supplied, so these are trace-mapped statuses, not independently verified per-case logs. |
| Manual / MySQL status | **Not Executed** | All 10 manual cases remain Not Executed. This includes S1-M-DB-01 through S1-M-DB-04; no MySQL result is claimed. |
| API and test-scope claims | **No new unsupported feature claim identified** | The final catalog continues to distinguish SQLite pytest coverage from MySQL manual cases and does not claim frontend/backend/database integration execution. |
| Reported test summary | **Recorded** | Python 3.11.18, pytest 8.3.4, 84 passed, 0 failed, 1 deprecation warning, 77.13 seconds. Warning text and run output were not supplied. |

### Historical findings disposition

- The finalized catalog added formal cases for duplicate email, case-insensitive email, Admin self-registration, unknown patient lookup, unknown prescription lookup, and whitespace-only registration names. The earlier “unmapped existing pytest cases” finding is addressed for the added automated scenarios.
- The catalog reflects the earlier recommendations to narrow SRS mappings, distinguish implementation-derived behaviour, narrow manual input scope, and use model-compatible schema expectations for backend-calling MySQL cases. The MySQL cases remain plans only and have not been executed.
- The earlier static finding about two-space registration names remains an **unverified defect candidate** in S1-M-INPUT-03. No manual execution result is available.
- Missing direct assertions for database side effects after rejected requests, MySQL constraints/persistence/failure handling, frontend integration, and system-wide requirement coverage remain coverage limitations. The aggregate pytest pass does not close these gaps.

