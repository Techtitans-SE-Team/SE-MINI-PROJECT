"""Shared protection for rate-limited third-party services (Google Translate, Google TTS).

* calls are spaced out (a burst of requests is what triggers HTTP 429 "Too Many Requests"),
* temporary failures are retried with exponential backoff,
* once retries are exhausted on a 429 the service is left alone for a cool-down period instead of
  being hammered further, and callers get a clean ServiceUnavailable instead of a crash.
"""
import logging
import threading
import time

from ..config import get_settings

log = logging.getLogger(__name__)

RATE_LIMITED, TRANSIENT = "rate_limited", "transient"


class ServiceUnavailable(Exception):
    """The external service could not be used right now (rate limited, offline or failing)."""


class ServiceGuard:
    def __init__(self, name: str):
        self.name = name
        self._lock = threading.Lock()
        self._last_call = 0.0
        self._blocked_until = 0.0

    def reset(self) -> None:
        self._last_call = self._blocked_until = 0.0

    def _space_calls(self, interval: float) -> None:
        if interval <= 0:
            return
        with self._lock:
            wait = self._last_call + interval - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self._last_call = time.monotonic()

    def call(self, fn, classify):
        """Run fn(). classify(exc) returns RATE_LIMITED, TRANSIENT or None (None = not retryable, re-raised)."""
        cfg = get_settings()
        remaining = self._blocked_until - time.monotonic()
        if remaining > 0:
            raise ServiceUnavailable(f"{self.name} is rate limited; try again in about {int(remaining) + 1} seconds")

        last_kind = TRANSIENT
        for attempt in range(cfg.EXTERNAL_MAX_RETRIES + 1):
            self._space_calls(cfg.EXTERNAL_MIN_INTERVAL)
            try:
                return fn()
            except Exception as exc:  # noqa: BLE001 - classified below
                kind = classify(exc)
                if kind is None:
                    raise
                last_kind = kind
                log.warning("%s call failed (%s), attempt %d/%d: %s", self.name, kind, attempt + 1,
                            cfg.EXTERNAL_MAX_RETRIES + 1, exc)
                if attempt < cfg.EXTERNAL_MAX_RETRIES:
                    time.sleep(cfg.EXTERNAL_BASE_DELAY * (2 ** attempt))

        if last_kind == RATE_LIMITED:
            self._blocked_until = time.monotonic() + cfg.EXTERNAL_COOLDOWN_SECONDS
            raise ServiceUnavailable(f"{self.name} is rate limited (too many requests). Try again in a minute")
        raise ServiceUnavailable(f"{self.name} is not reachable right now. Check the internet connection and retry")
