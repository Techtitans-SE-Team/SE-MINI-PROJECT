from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/doctor_reminder_db"
    SECRET_KEY: str = "dev-only-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_MB: int = 5
    AUTO_CREATE_TABLES: bool = False

    # --- Multilingual media (translation, TTS, video) ---
    MEDIA_DIR: str = "media"
    AUTO_GENERATE_MEDIA: bool = True        # generate audio/video in the background when a prescription is verified
    FFMPEG_PATH: str = ""                   # optional; defaults to the ffmpeg bundled with imageio-ffmpeg
    # External services (Google Translate / Google TTS) are rate limited, so calls are retried with backoff
    EXTERNAL_MAX_RETRIES: int = 3
    EXTERNAL_BASE_DELAY: float = 1.5        # seconds; doubled on every retry
    EXTERNAL_MIN_INTERVAL: float = 0.4      # minimum gap between two calls to the same service
    EXTERNAL_COOLDOWN_SECONDS: int = 60     # after retries are exhausted on a 429, stop calling for this long

    # --- Reminders / notifications ---
    TIMEZONE: str = "Asia/Kolkata"
    ENABLE_SCHEDULER: bool = True           # background loop that turns due reminders into notifications
    SCHEDULER_INTERVAL_SECONDS: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
