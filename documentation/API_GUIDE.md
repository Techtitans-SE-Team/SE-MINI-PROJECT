# Backend API Guide (for Frontend – Member 2)

**Base URL (local):** `http://localhost:8000`
**Interactive docs (try every endpoint):** `http://localhost:8000/docs`
**CORS:** allowed for `http://localhost:3000` and `http://localhost:5173` (change `CORS_ORIGINS` in backend `.env` if your React port differs).

## 1. Authentication

1. Call `POST /auth/login` → you get an `access_token`.
2. Send it on every other request: `Authorization: Bearer <access_token>`
3. Token expires after 60 minutes → backend returns **401**; send the user back to the login page.
4. Role comes back in the login response (`Patient`, `Doctor`, `Admin`). Use it to choose the dashboard.

Roles: **Patient** and **Doctor** self-register. **Admin** accounts cannot be registered from the UI (created by script by the backend owner).

### POST /auth/register  (public)
Patient:
```json
{
  "name": "Ravi Kumar",
  "email": "ravi@example.com",
  "password": "Passw0rdX",
  "role": "Patient",
  "date_of_birth": "1998-05-14",
  "phone": "9876543210",
  "preferred_language": "Hindi",
  "address": "Bengaluru"
}
```
Doctor:
```json
{
  "name": "Dr Meera Rao",
  "email": "meera@example.com",
  "password": "Passw0rdX",
  "role": "Doctor",
  "specialization": "Cardiology",
  "qualification": "MBBS, MD",
  "license_number": "KA12345"
}
```
Rules: name 2–100 chars; password 8–72 chars with an uppercase, a lowercase and a digit; phone 10–14 digits (optional leading `+`); date_of_birth must be in the past.
Required for Patient: `date_of_birth`, `phone`, `preferred_language`. Required for Doctor: `specialization`. Optional: `address`, `qualification`, `license_number`.

**201 response:**
```json
{ "user_id": 7, "name": "Ravi Kumar", "email": "ravi@example.com", "role_name": "Patient", "created_at": "2026-11-16T10:00:00" }
```
Errors: **409** email already registered / license already registered, **422** validation.

### POST /auth/login  (public)
```json
{ "email": "ravi@example.com", "password": "Passw0rdX" }
```
**200 response:**
```json
{ "access_token": "eyJ...", "token_type": "bearer", "user_id": 7, "name": "Ravi Kumar", "role": "Patient" }
```
Error: **401** `"Incorrect email or password"` (same message for unknown email and wrong password).

### GET /auth/me  (any logged-in user)
Returns the same shape as the register response.

## 2. Patients

| Method | Path | Who | Notes |
|---|---|---|---|
| GET | `/patients/me` | Patient | Own profile |
| PUT | `/patients/me` | Patient | Update profile (all fields optional) |
| GET | `/patients?search=ravi` | Doctor / Admin | All active patients: `[{patient_id, name, preferred_language}]`, optional `search` by name. Use it for the doctor's "pick a patient" dropdown |
| GET | `/patients/{patient_id}` | Doctor (only after prescribing for that patient) / Patient (self) / Admin | Full profile |

Patient object:
```json
{ "patient_id": 3, "user_id": 7, "name": "Ravi Kumar", "email": "ravi@example.com",
  "date_of_birth": "1998-05-14", "phone": "9876543210", "preferred_language": "Hindi",
  "address": "Bengaluru", "status": "Active" }
```
`PUT /patients/me` body (send only what changed): `name`, `date_of_birth`, `phone`, `preferred_language`, `address`.

## 3. Prescriptions

Prescription object (`PrescriptionOut`):
```json
{
  "prescription_id": 12, "patient_id": 3, "doctor_id": 2,
  "patient_name": "Ravi Kumar", "doctor_name": "Dr Meera Rao",
  "medicine_name": "Paracetamol", "dosage": "500 mg", "frequency": "Twice daily", "duration": "5 days",
  "instructions": null, "prescription_date": "2026-11-16",
  "verification_status": "Pending",
  "processing_status": "Pending Verification",
  "status": "Active",
  "created_at": "2026-11-16T10:05:00",
  "medicines": [ { "medicine_id": 1, "prescription_id": 12, "medicine_name": "Paracetamol", "dosage": "500 mg",
                   "frequency": "Twice daily", "duration": "5 days", "instructions": null,
                   "extraction_status": "Confirmed" } ],
  "files": [ { "file_id": 1, "prescription_id": 12, "original_file_name": "rx.jpg", "file_type": "jpg",
               "file_size": 120345, "upload_date": "2026-11-16T10:05:00", "upload_status": "Processed" } ]
}
```
Statuses:
- `processing_status`: Uploaded → Processing → Pending Verification → Verified / Rejected
- `extraction_status` (per medicine): Extracted, Needs Review (some field = "Not detected"), Confirmed
- `status`: Active / Completed / Cancelled

**Visibility:** a Patient only sees prescriptions that are **Verified**. Doctors see their own. Admin sees all.

| Method | Path | Who | Purpose |
|---|---|---|---|
| POST | `/prescriptions` | Doctor | Manual entry (form below) |
| GET | `/prescriptions` | Any | List (filtered by role automatically) |
| GET | `/prescriptions/{id}` | Doctor (own) / Patient (own, verified) / Admin | Detail |
| PUT | `/prescriptions/{id}` | Doctor (own) | Edit fields or `status`; verified prescriptions cannot be edited (409) |
| POST | `/prescriptions/upload` | Doctor | Upload file + OCR (below) |
| POST | `/prescriptions/{id}/reprocess` | Doctor | Re-run OCR on the stored file |
| GET | `/prescriptions/{id}/file` | Authorized users | Download the original file |
| GET | `/prescriptions/{id}/medicines` | Authorized users | List medicines |
| POST | `/prescriptions/{id}/medicines` | Doctor | Add a medicine |
| PUT | `/prescriptions/{id}/medicines/{medicine_id}` | Doctor | Correct OCR output |
| DELETE | `/prescriptions/{id}/medicines/{medicine_id}` | Doctor | Remove (204, no body) |
| POST | `/prescriptions/{id}/verify` | Doctor | Verify or reject |

### POST /prescriptions  (manual entry)
```json
{ "patient_id": 3, "prescription_date": "2026-11-16", "medicine_name": "Amoxicillin",
  "dosage": "250 mg", "frequency": "1-0-1", "duration": "7 days", "instructions": "After food" }
```
All fields except `instructions` are required; date cannot be in the future. Created as verification "Pending".

### POST /prescriptions/upload  (multipart/form-data, NOT JSON)
Fields: `patient_id` (required), `prescription_date` (optional, defaults to today), `file` (required: jpg, jpeg, png or pdf, max 5 MB).
```js
const fd = new FormData();
fd.append("patient_id", 3);
fd.append("file", fileInput.files[0]);
fetch("http://localhost:8000/prescriptions/upload", {
  method: "POST",
  headers: { Authorization: `Bearer ${token}` },   // do NOT set Content-Type yourself
  body: fd,
});
```
**201 response** = the prescription object above plus:
```json
{ "ocr_status": "success", "message": "2 medicine(s) extracted; 1 need review because some details are missing" }
```
`ocr_status` is `success`, `no_medicines_found` (let the doctor add medicines manually) or `failed`.
Show `message` to the doctor. Fields reading `"Not detected"` must be highlighted for correction.

### PUT /prescriptions/{id}/medicines/{medicine_id}
Send only changed fields: `medicine_name`, `dosage`, `frequency`, `duration`, `instructions`.

### POST /prescriptions/{id}/verify
```json
{ "action": "verify" }      // or "reject"; body is optional, default is verify
```
Returns the updated prescription. After verification the patient can see it and it is locked from edits.

## 4. Admin (Admin only)
- `GET /admin/users` → list of users (same shape as register response)
- `GET /admin/stats` → `{users, patients, doctors, prescriptions}` counts for the admin dashboard

## 5. Errors
All errors are JSON:
```json
{ "detail": "You do not have permission to perform this action" }
```
| Code | Meaning | Frontend action |
|---|---|---|
| 401 | Missing/expired token or bad login | Go to login |
| 403 | Wrong role / not your record | Show "not allowed" |
| 404 | Not found | Show not-found message |
| 409 | Duplicate email/license, or editing a verified prescription | Show `detail` |
| 422 | Validation failed | `detail` is a **list**: `[{ "loc": ["body","phone"], "msg": "..." }]` → show `msg` under the field named by the last item of `loc` |

For 401/403/404/409, `detail` is a string. Only 422 returns a list.

## 6. Quick test flow
1. Register a Patient and a Doctor (UI or `/docs`).
2. Log in as the Doctor, call `GET /patients` to get the `patient_id`.
3. Upload or create a prescription for that patient, then verify it.
4. Log in as the Patient: `GET /prescriptions` now shows it (patients only see verified ones).

`GET /admin/stats` returns `{ "users": n, "patients": n, "doctors": n, "prescriptions": n }`.

## 7. Reminders, translated instructions, audio/video and notifications (new)

**Flow for the patient screen:** doctor verifies a prescription -> backend automatically builds the translated instruction, audio and video in the patient's preferred language -> patient opens it from `GET /prescriptions/{id}/media`.

### Media item
```json
{ "media_id": 4, "prescription_id": 12, "medicine_id": 9, "language_code": "kn", "language_name": "Kannada",
  "source_text": "Take Paracetamol, 500 mg, Twice daily, for 5 days. After food.",
  "translated_text": "...", "translated": true, "has_audio": true, "has_video": true,
  "status": "Completed", "message": null }
```
`status`: **Completed**, **Partial** (something fell back, read `message`, e.g. translation was rate limited so English is shown) or **Failed**. Show `translated_text`; play the files only when `has_audio` / `has_video` is true.

| Method | Path | Who | Notes |
|---|---|---|---|
| GET | `/languages` | public | `[{name, code}]` for the language dropdown |
| POST | `/prescriptions/{id}/media?language=Hindi` | Doctor (own) / Patient (own, verified) | Generates (or returns existing) items; language optional. 409 if not verified, 422 if unsupported |
| GET | `/prescriptions/{id}/media` | same as prescription | List items |
| GET | `/media/{media_id}/video` | same as prescription | MP4. Use `fetch` with the Authorization header and `URL.createObjectURL(blob)` for `<video src>` (a plain `<video src>` cannot send the token) |
| GET | `/media/{media_id}/audio` | same | MP3, same approach |

### Reminders (Patient only)
| Method | Path | Body / notes |
|---|---|---|
| POST | `/reminders` | `{ "medicine_id": 9, "reminder_time": "08:00:00" }`, 409 if the same time already exists |
| POST | `/reminders/auto/{prescription_id}` | Creates times from the frequency. Returns `{ "created": [...], "needs_manual_time": ["MedicineName"] }` |
| GET | `/reminders` | list; `/reminders/due` = active reminders whose time has passed today |
| PATCH | `/reminders/{id}` | `{ "reminder_time": "09:00:00" }` and/or `{ "is_active": false }` |
| DELETE | `/reminders/{id}` | 204 |

### Notifications (Patient only)
Notification: `{ notification_id, reminder_id, medicine_id, media_id, message, notify_date, reminder_time, status: "Unread"|"Read" }`
- `POST /notifications/check` -> `{ "created": n }` — call every minute while the app is open.
- `GET /notifications?unread_only=true` — show badge/list; `media_id` (if set) lets you open the video.
- `POST /notifications/{id}/read`.
