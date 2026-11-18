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

## Multilingual instructions, audio, video, reminders and notifications
Flow: Verified prescription -> translated instruction -> audio (TTS) -> short MP4 video -> reminder -> notification.

| Method | Path | Purpose |
|---|---|---|
| GET | /languages | Supported languages (English, Hindi, Marathi, Kannada, Tamil, Telugu, Malayalam, Bengali, Gujarati, Punjabi) |
| POST | /prescriptions/{id}/media?language=Hindi&regenerate=false | Translate + audio + video for each medicine (verified prescriptions only; language defaults to the patient's preferred language) |
| GET | /prescriptions/{id}/media | List generated items |
| GET | /media/{media_id}/audio , /media/{media_id}/video | Stream MP3 / MP4 (same access rules as the prescription) |
| POST | /reminders | Create a reminder for a medicine (409 if duplicate) |
| POST | /reminders/auto/{prescription_id} | Create reminders from the frequency (1-0-1, BD, TDS, Twice daily ...) |
| GET | /reminders, /reminders/due | List / due now |
| PATCH, DELETE | /reminders/{id} | Change time / switch off / delete |
| GET | /notifications?unread_only=true | Patient notifications |
| POST | /notifications/check | Create notifications for reminders due now (poll every minute) |
| POST | /notifications/{id}/read | Mark read |

Verifying a prescription automatically starts media generation in the background for the patient's language.
A background scheduler (ENABLE_SCHEDULER) also turns due reminders into notifications every minute (one per reminder per day).

### Google Translate / TTS rate limits ("TooManyRequests")
Both services are free Google endpoints with request limits. The backend now:
1. spaces calls (EXTERNAL_MIN_INTERVAL) and retries with exponential backoff (EXTERNAL_MAX_RETRIES, EXTERNAL_BASE_DELAY),
2. pauses the service for EXTERNAL_COOLDOWN_SECONDS after repeated 429 errors instead of hammering it,
3. caches translations and reuses finished items (only Partial/Failed items are retried),
4. never crashes: if translation is unavailable the English text is used and the item is marked `Partial` with an explanatory `message`; if audio fails the video is still made (silent) and the text is kept.
Needs internet access. ffmpeg is bundled (imageio-ffmpeg), fonts for all scripts are bundled in `app/assets/fonts` (Noto, OFL licence).

Run the SQL scripts `database/schema/09_*.sql`, `10_*.sql`, `11_*.sql` after the earlier ones (or use AUTO_CREATE_TABLES=true for local dev).
