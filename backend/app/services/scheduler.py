"""Turns due medicine reminders into in-app notifications (one per reminder per day)."""
import asyncio
import logging
import re
from datetime import datetime, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import InstructionMedia, Medicine, MedicineReminder, Notification, Patient
from .languages import resolve_language

log = logging.getLogger(__name__)


def now_local() -> datetime:
    try:
        return datetime.now(ZoneInfo(get_settings().TIMEZONE))
    except ZoneInfoNotFoundError:
        return datetime.now()


# ---------------------------------------------------------------- default times from a frequency string
_SLOTS = {1: [time(8)], 2: [time(8), time(20)], 3: [time(8), time(14), time(20)], 4: [time(8), time(12), time(16), time(20)]}
_WORDS = {"once": 1, "one": 1, "twice": 2, "two": 2, "thrice": 3, "three": 3, "four": 4}
_ABBR = {"od": 1, "qd": 1, "bd": 2, "bid": 2, "tds": 3, "tid": 3, "qid": 4, "qds": 4}


def suggest_times(frequency: str) -> list[time]:
    """'1-0-1' -> morning+night, 'Twice daily' -> 08:00/20:00, 'TDS' -> 3 slots. Empty list if unknown."""
    f = (frequency or "").strip().lower()
    m = re.match(r"^(\d)\s*-\s*(\d)\s*-\s*(\d)(?:\s*-\s*(\d))?", f)
    if m:
        parts = [int(x) for x in m.groups() if x is not None]
        if len(parts) == 3:
            slots = [time(8), time(14), time(21)]
        else:
            slots = [time(8), time(13), time(18), time(22)]
        return [t for t, n in zip(slots, parts) if n > 0]
    if re.search(r"\b(hs|at night|bedtime)\b", f):
        return [time(21)]
    for token in re.findall(r"[a-z]+", f):
        if token in _ABBR:
            return list(_SLOTS[_ABBR[token]])
    for word, n in _WORDS.items():
        if re.search(rf"\b{word}\b", f):
            return list(_SLOTS[n])
    m = re.search(r"\b(\d)\s*(?:x|times)\b", f)
    if m and int(m.group(1)) in _SLOTS:
        return list(_SLOTS[int(m.group(1))])
    if "daily" in f or "morning" in f or "every day" in f:
        return list(_SLOTS[1])
    return []


# ---------------------------------------------------------------- notification creation
def _message(db: Session, patient: Patient, med: Medicine) -> tuple[str, int | None]:
    lang = resolve_language(patient.preferred_language)
    media = None
    if lang:
        media = db.scalar(select(InstructionMedia).where(InstructionMedia.medicine_id == med.medicine_id,
                                                         InstructionMedia.language_code == lang.code))
    if media:
        return media.translated_text, media.media_id
    return f"Time to take {med.medicine_name}, {med.dosage} ({med.frequency}).", None


def process_due_reminders(db: Session, patient_id: int | None = None, now: datetime | None = None) -> int:
    """Create today's notification for every active reminder whose time has passed. Returns how many were created."""
    now = now or now_local()
    stmt = select(MedicineReminder).where(MedicineReminder.is_active.is_(True),
                                          MedicineReminder.reminder_time <= now.time())
    if patient_id is not None:
        stmt = stmt.where(MedicineReminder.patient_id == patient_id)
    created = 0
    for rem in db.scalars(stmt).all():
        exists = db.scalar(select(Notification.notification_id).where(
            Notification.reminder_id == rem.reminder_id, Notification.notify_date == now.date()))
        med = db.get(Medicine, rem.medicine_id)
        if exists or med is None:
            continue
        text, media_id = _message(db, db.get(Patient, rem.patient_id), med)
        db.add(Notification(patient_id=rem.patient_id, reminder_id=rem.reminder_id, medicine_id=med.medicine_id,
                            media_id=media_id, message=text, notify_date=now.date(), reminder_time=rem.reminder_time))
        try:
            db.commit()
            created += 1
        except IntegrityError:  # another worker created it first
            db.rollback()
    return created


async def scheduler_loop(session_factory) -> None:
    interval = get_settings().SCHEDULER_INTERVAL_SECONDS
    while True:
        try:
            def work():
                with session_factory() as db:
                    return process_due_reminders(db)
            n = await asyncio.to_thread(work)
            if n:
                log.info("Created %d reminder notification(s)", n)
        except Exception:  # noqa: BLE001 - the loop must survive any error
            log.exception("Reminder scheduler iteration failed")
        await asyncio.sleep(interval)
