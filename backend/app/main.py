
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from . import models
from .config import get_settings
from .database import Base, SessionLocal, engine
from .routers import admin, auth, media, notifications, patients, prescriptions, reminders
from .services.scheduler import scheduler_loop

settings = get_settings()


def init_db():
    if settings.AUTO_CREATE_TABLES:
        Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        existing = set(db.scalars(select(models.Role.role_name)))

        for name in (
            models.ROLE_DOCTOR,
            models.ROLE_PATIENT,
            models.ROLE_ADMIN,
        ):
            if name not in existing:
                db.add(models.Role(role_name=name))

        db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    task = asyncio.create_task(scheduler_loop(SessionLocal)) if settings.ENABLE_SCHEDULER else None
    yield
    if task:
        task.cancel()


app = FastAPI(
    title="Doctor Prescription Reminder API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(prescriptions.router)
app.include_router(admin.router)
app.include_router(reminders.router)
app.include_router(media.router)
app.include_router(notifications.router)


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}
