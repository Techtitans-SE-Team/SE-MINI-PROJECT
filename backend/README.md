# Backend – Doctor Prescription Reminder (Member 1)

FastAPI + SQLAlchemy backend on the MySQL schema in `/database/schema` (Member 3).

## Run
```bash
cd backend
python -m venv venv && source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # set DATABASE_URL and SECRET_KEY
# run the SQL scripts in /database/schema first (01 -> 08)
python -m scripts.create_admin "Admin" admin@example.com 'Admin@12345'
uvicorn app.main:app --reload                          # docs at http://localhost:8000/docs
pytest                                                 # 84 tests, uses in-memory SQLite
```
OCR needs the **Tesseract** binary (Windows: UB-Mannheim installer, Ubuntu: `apt install tesseract-ocr`). Scanned PDFs also need **poppler**. If OCR is unavailable the upload still succeeds, the file is marked `Failed` and the doctor enters medicines manually.

## Sprint 1 – APIs
| Method | Path | Who | Purpose |
|---|---|---|---|
| POST | /auth/register | public | Register Patient or Doctor (Admin cannot self-register) |
| POST | /auth/login | public | Returns JWT + role |
| GET | /auth/me | any | Current user |
| GET/PUT | /patients/me | Patient | View / update own profile |
| GET | /patients?search= | Doctor, Admin | Patient picker (name + language only) |
| GET | /patients/{id} | Admin, self, Doctor who prescribed | Full profile |
| POST | /prescriptions | Doctor | Create (always `Pending`) |
| GET | /prescriptions, /prescriptions/{id} | role-scoped | Doctor: own · Patient: own **verified** · Admin: all |
| PUT | /prescriptions/{id} | owning Doctor | Edit (blocked once verified) |
| POST | /prescriptions/{id}/verify | owning Doctor | `{"action": "verify"|"reject"}` |
| GET | /admin/users, /admin/stats | Admin | Admin dashboard data |

## Sprint 2 – APIs
| Method | Path | Purpose |
|---|---|---|
| POST | /prescriptions/upload | multipart: `patient_id`, `file` (jpg/png/pdf, ≤5 MB), optional `prescription_date`. Validates, stores, runs OCR, extracts medicines |
| POST | /prescriptions/{id}/reprocess | Re-run OCR on the stored file |
| GET | /prescriptions/{id}/file | Download the uploaded file (authorised users only) |
| GET/POST | /prescriptions/{id}/medicines | List extracted / add manual medicine |
| PUT/DELETE | /prescriptions/{id}/medicines/{mid} | Doctor corrects extracted data |

Status flow: `Uploaded → Processing → Pending Verification → Verified | Rejected`. Medicines with any missing field are `Needs Review`; verification is refused (409) until every medicine is corrected/confirmed.

## Design notes / assumptions
- Passwords: bcrypt. Tokens: JWT (60 min). Same error for unknown email and wrong password.
- A patient can only see their prescriptions after a doctor verifies them.
- The `prescriptions` row mirrors its first medicine; all medicines live in `medicines`.
- Uploaded files are stored under random names, with type checked by extension **and** magic bytes.
