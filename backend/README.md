# Backend (FastAPI) – Member 1

## Setup
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # set DATABASE_URL and SECRET_KEY
# OCR needs the Tesseract binary: https://github.com/tesseract-ocr/tesseract (and Poppler for scanned PDFs)
python scripts/create_admin.py      # create first admin
uvicorn app.main:app --reload       # docs at http://localhost:8000/docs
pytest                              # run tests (uses in-memory SQLite)
```
Database tables come from `database/schema/*.sql` (run in order). Set `AUTO_CREATE_TABLES=true` only for local dev.

## Sprint 1 APIs
| Method | Path | Access |
|---|---|---|
| POST | /auth/register | public (patient/doctor) |
| POST | /auth/login | public, returns JWT + role |
| GET | /auth/me | authenticated |
| GET/PUT | /patients/me | patient |
| GET | /patients, /patients/{id} | doctor (own patients) / admin |
| GET | /admin/users, /admin/stats | admin |
| POST/GET/PUT | /prescriptions, /prescriptions/{id} | doctor / patient (own) |

## Sprint 2 APIs (upload + OCR + verification)
| Method | Path | Purpose |
|---|---|---|
| POST | /prescriptions/upload | Upload PDF/JPG/PNG (validated type + size), runs OCR, extracts medicine name, dosage, frequency, duration |
| POST | /prescriptions/{id}/reprocess | Re-run OCR |
| GET | /prescriptions/{id}/file | Download original file (authorized users only) |
| GET/POST | /prescriptions/{id}/medicines | List / add extracted medicines |
| PUT/DELETE | /prescriptions/{id}/medicines/{mid} | Doctor corrects extracted data |
| POST | /prescriptions/{id}/verify | Doctor verifies (status → Verified) |

Statuses: Uploaded → Processing → Pending Verification → Verified / Rejected.
Dosage text is preserved exactly as written; incomplete extractions are flagged for doctor review.
