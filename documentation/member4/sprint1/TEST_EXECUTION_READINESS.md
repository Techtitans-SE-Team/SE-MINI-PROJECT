# Sprint 1 Test Execution Readiness

**Project:** Doctor Prescription to Multilingual Video Reminder and Instruction Generator  
**Scope:** Existing backend pytest suite and the Sprint 1 manual database cases  
**Inspection date:** 2026-11-17  
**Execution status:** User-reported automated backend suite completed successfully: 84 passed, 0 failed, 1 deprecation warning, 75.76 seconds. No tests were rerun while updating this report. No MySQL or frontend/backend/database integration run is claimed.

## 1. Readiness summary

The checked-in backend pytest suite is designed to use an isolated in-memory SQLite database. Its `backend/tests/conftest.py` sets test-process environment values before importing the application, creates a dedicated SQLite `StaticPool` engine, drops and recreates that engine's tables for each `db` fixture, inserts test roles, and overrides the application's `get_db` dependency. The tests use FastAPI's `TestClient`; their database operations are served from the fixture database, not the configured MySQL server.

The automated run used Python 3.11.18, pytest 8.3.4, and the project virtual environment at `backend/.venv`. The project dependencies are installed there; package metadata was checked without running tests. The user-reported suite result is 84 passed, 0 failed, 1 deprecation warning, in 75.76 seconds. No `backend/.env` is present. This does not establish compatibility with Python 3.14.

The four MySQL-dependent cases in the Sprint 1 test catalog (`S1-M-DB-01` through `S1-M-DB-04`) are manual database scenarios, not existing pytest tests, and remain Not Executed. They require a deliberately provisioned, disposable MySQL database. Do not direct them to a development or production database.

## 2. Verified repository and environment facts

| Area | Verified fact |
|---|---|
| Pytest configuration | `backend/pytest.ini` sets `testpaths = tests`; no other pytest options are configured there. |
| Test files | `test_auth.py`, `test_patients_rbac.py`, `test_prescriptions.py`, `test_upload_ocr.py`, and `test_extraction.py`, plus shared `conftest.py`. |
| SQLite fixture | `conftest.py` sets `DATABASE_URL=sqlite://`, `AUTO_CREATE_TABLES=true`, and a test secret before application imports; it creates a separate in-memory SQLite engine with `StaticPool`. |
| Per-test database lifecycle | The `db` fixture calls `drop_all` and `create_all` on the fixture engine, inserts Doctor/Patient/Admin roles, and yields a session. `client` overrides `get_db` to use that session. |
| Uploaded files | The `client` fixture sets `UPLOAD_DIR` to a per-test `tmp_path` location. Upload tests therefore use temporary test files, not the default project upload directory. |
| App default database | `backend/app/config.py` defaults to `mysql+pymysql://root:password@localhost:3306/doctor_reminder_db`; the app's default `AUTO_CREATE_TABLES` is false. `backend/.env.example` also names `doctor_reminder_db`. |
| Local environment | `backend/.venv` is present and was used for the reported run. No `backend/.env` is present. Secret values were not read or reported. |
| Test Python | `backend/.venv/bin/python` reports Python 3.11.18; `backend/.venv` contains pytest 8.3.4 and the declared backend Python packages. Package metadata was inspected without executing tests. |
| MySQL tools | `mysql` and `mysqld` executables are on PATH. This confirms client/server binaries exist, not that a server is running or that a safe test database exists. Server status and credentials were not checked. |
| OCR system tools | `tesseract` and `pdftoppm` were not found on PATH. |
| CI workflow | No `.github` directory/workflow files were present in this checkout. |

## 3. Existing test inventory and database/service requirements

| Test file | Main coverage | Database / external service needs for checked-in tests |
|---|---|---|
| `backend/tests/test_auth.py` | Patient/Doctor registration, duplicate/case-insensitive email, admin self-registration rejection, validation, password hashing, login, token-protected identity | SQLite fixture only; no external service. |
| `backend/tests/test_patients_rbac.py` | Patient profile read/update and validation, authentication and role gates, patient/doctor/admin access, unknown patient lookup | SQLite fixture only; no external service. |
| `backend/tests/test_prescriptions.py` | Manual prescription create/update, dosage preservation, required/blank field validation, date/patient validation, prescription visibility and ownership, verification/rejection, unknown prescription | SQLite fixture only; no external service. |
| `backend/tests/test_upload_ocr.py` | Upload validation and permissions, OCR result handling, medicine extraction, verification/correction, file naming and access | SQLite fixture and temporary files. Most OCR behavior is monkeypatched. The embedded-text PDF test uses `pypdf`; it does not require Tesseract/Poppler when text extraction succeeds. Image/scanned-PDF OCR requires OS tools if tested without a mock. |
| `backend/tests/test_extraction.py` | Pure rule-based parsing of medicine, dosage, frequency, duration, instructions, missing fields, and multiple/empty lines | No database, network, or OCR binary; application Python dependencies still need to import. |

### SQLite versus MySQL

- All existing pytest tests are configured to use the in-memory SQLite fixture. No checked-in pytest test connects to MySQL by design in the inspected `conftest.py` and test modules.
- The four manual Sprint 1 database cases are MySQL-dependent: schema/constraints (`S1-M-DB-01`), persistence across sessions (`S1-M-DB-02`), direct SQL constraint enforcement (`S1-M-DB-03`), and backend write-failure handling (`S1-M-DB-04`).
- `S1-M-DB-02` and `S1-M-DB-04` call the backend and require a schema compatible with current ORM models, documented as schema scripts 01–08 or equivalent. `S1-M-DB-01` and `S1-M-DB-03` are SQL-only Sprint 1 schema checks using scripts 01–05, as specified in the test catalog.
- No MySQL-dependent manual case should run against a shared development or production database. Use a separately named disposable database and a dedicated test account/credentials after verifying the connection target.

## 4. Data safety assessment

### Verified safeguards in the current pytest setup

1. `conftest.py` sets the pytest process's `DATABASE_URL` to `sqlite://` before importing `app.database` and `app.main`.
2. The tests use their own `create_engine("sqlite://", ...)` fixture engine and override `get_db` for client requests.
3. Each test database fixture drops and recreates tables only on that fixture engine; it is an in-memory database.
4. Upload tests direct files to pytest's temporary directory through `tmp_path`.
5. No checked-in pytest fixture runs the MySQL schema scripts or inserts into MySQL.

### Conditions and residual risks

- These safeguards apply when pytest is started with the repository's `backend/tests/conftest.py` loaded. Run pytest from `backend/` (or explicitly point pytest at `tests/`) so the intended conftest is discovered.
- Do not change/remove the environment overrides, bypass the fixture, or run application setup scripts such as `scripts/create_admin.py` as part of test execution.
- `DATABASE_URL` is also the application's normal database setting. Before any future manual MySQL run, inspect the effective connection target without exposing credentials; never rely on the default/example database name as proof that the target is disposable.
- The inspected code and fixture direct pytest requests to the in-memory SQLite fixture. The aggregate execution summary does not include connection logs, so this report does not claim to verify a runtime MySQL connection target.
- The MySQL manual cases can alter schema/data. Their safety depends on a newly provisioned disposable database and controlled failure setup; this was not verified because no MySQL connection or data operation was attempted.

## 5. Environment variables and service requirements

### Variables set by pytest fixture

| Variable | Test value / purpose |
|---|---|
| `DATABASE_URL` | `sqlite://`, selected before application import. |
| `AUTO_CREATE_TABLES` | `true` for the application settings initialized during pytest import. |
| `SECRET_KEY` | `test-secret`; test-only token signing key. |
| `UPLOAD_DIR` | Replaced for each client fixture with a `tmp_path` upload folder. |

The backend settings also define `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, CORS origins, and upload size, but the tests do not require a `.env` file for their standard fixture setup. No credentials or secret values from an actual `.env` file were inspected because none was present.

### Dependencies and services

- Python packages: dependencies from `backend/requirements.txt` are installed in `backend/.venv`; inspected package metadata includes pytest 8.3.4, FastAPI 0.115.6, SQLAlchemy 2.0.36, PyMySQL 1.1.1, pydantic-settings 2.7.0, httpx 0.28.1, pypdf 7.1.0, pytesseract 0.3.13, Pillow 13.0.0, and pdf2image 1.17.0.
- SQLite: supplied through Python's standard library; no separate SQLite server is required.
- MySQL server: not required for the pytest suite; required only for the manual MySQL cases.
- Tesseract: required for real image OCR and scanned-PDF OCR. It was not found on PATH.
- Poppler (`pdftoppm`): required by `pdf2image` for scanned-PDF rendering. It was not found on PATH.
- `pypdf`: used by PDF embedded-text extraction and installed in `backend/.venv` (7.1.0).
- Network/external APIs: no external network service is used by the inspected tests.

## 6. Missing setup and compatibility checks

1. The isolated `backend/.venv` exists and has the required Python packages installed. The reported run completed in this environment.
2. Python 3.11.18 and pytest 8.3.4 are verified for the reported execution. The repository does not declare its supported Python range; compatibility outside this tested version (including Python 3.14.7) remains **unverified**.
3. `backend/.env` is absent. It is not needed for the configured pytest fixture, but it may be needed for normal local app operation or MySQL manual cases. Do not create or copy a production `.env` for pytest.
4. MySQL server binaries are present, but service availability, database existence, schema version, credentials, and disposable-database isolation are **unverified**.
5. Tesseract and Poppler executables are absent from PATH. The checked-in tests mostly mock OCR and the embedded-text PDF case uses `pypdf`; real image/scanned-PDF OCR is not ready without those system packages.
6. No GitHub Actions workflow was found, so automated CI execution is not configured in the inspected checkout.

Environment used for the reported run (the suite was not rerun during this documentation update):

```text
Interpreter: backend/.venv/bin/python
Python: 3.11.18
pytest: 8.3.4
Dependencies: installed from backend/requirements.txt
Reported result: 84 passed, 0 failed, 1 deprecation warning, 75.76 seconds
```

## 7. Safe execution sequence

1. **Automated SQLite execution is complete per the user-reported result** under Python 3.11.18 and pytest 8.3.4 in `backend/.venv`; this documentation update did not rerun it.
2. For a future repeat, activate `backend/.venv` and run from `backend/` so `tests/conftest.py` is loaded. Collection-only inspection can confirm discovery without executing test functions.
3. **For any separate or future manual activity, review the target first.** Confirm `DATABASE_URL` will be overridden to SQLite by conftest, the temporary upload path is active, and no test helper or environment customization bypasses the fixtures. Do not run admin creation or database schema/sample-data scripts for the SQLite suite.
4. **Reported automated outcome:** the user reports the existing backend suite completed with 84 passed and 0 failed in 75.76 seconds. No category-by-category or per-test output was supplied; do not infer individual logs or broaden this result to manual/MySQL scenarios.
5. **Treat the OCR coverage accurately.** The standard suite's mocks and embedded-text PDF path do not establish that real Tesseract image OCR or scanned-PDF OCR works. Install/configure those OS tools only if real OCR execution is separately authorized and required.
6. **Schedule MySQL cases separately.** Provision a disposable database with a distinct test name and dedicated credentials; verify the target before setup. Run `S1-M-DB-01` and `S1-M-DB-03` as SQL-only checks against the documented Sprint 1 schema. Run `S1-M-DB-02` and `S1-M-DB-04` only against schema scripts 01–08 or an equivalent model-compatible disposable schema. Capture teardown/reset plan before writing data. Do not use development or production data.
7. **Keep evidence separated by environment.** The automated SQLite suite has the reported result above. Keep manual and MySQL cases Not Executed until separately run and evidenced; do not claim frontend/backend/database integration or real image/scanned-PDF OCR from the reported suite.

## 8. Readiness conclusion

- **Automated SQLite pytest suite:** **Executed successfully per user report** with Python 3.11.18 and pytest 8.3.4: 84 passed, 0 failed, 1 deprecation warning, 75.76 seconds. The terminal output was provided by the user and records the completed suite summary.
- **Manual MySQL cases:** **Not ready to execute** until a disposable schema-compatible test database, credentials, and safe failure-injection method are verified.
- **Real image/scanned-PDF OCR:** **Not ready** because Tesseract and Poppler are not on PATH; these are not prerequisites for every existing pytest case.
- **MySQL / frontend integration:** Not executed or claimed. Four manual MySQL cases remain Not Executed; the pytest fixture uses in-memory SQLite. No frontend-to-backend-to-database integration evidence was supplied.
