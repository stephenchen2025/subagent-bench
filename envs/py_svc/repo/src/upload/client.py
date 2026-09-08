"""Client for the object storage backend."""

import logging
import time
from dataclasses import dataclass

import urllib.error
import urllib.request

log = logging.getLogger(__name__)


@dataclass
class UploadResult:
    key: str
    attempts: int
    ok: bool


class UploadClient:
    """Uploads objects to the storage backend.

    Settings come from settings/upload.yml, with one exception: the retry
    behaviour below is not configurable.
    """

    def __init__(self, endpoint, timeout_seconds=30):
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds

    def _put(self, key, payload):
        req = urllib.request.Request(
            f"{self.endpoint}/{key}", data=payload, method="PUT"
        )
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
            return resp.status

    def upload(self, key, payload):
        """Upload a single object, retrying on transient failures."""
        last_error = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                status = self._put(key, payload)
                return UploadResult(key=key, attempts=attempt, ok=status < 300)
            except urllib.error.URLError as exc:
                last_error = exc
                log.warning("upload %s attempt %d failed: %s", key, attempt, exc)
                time.sleep(RETRY_INTERVAL_SECONDS)
        log.error("upload %s exhausted %d attempts: %s", key, MAX_ATTEMPTS, last_error)
        return UploadResult(key=key, attempts=MAX_ATTEMPTS, ok=False)


# Retry policy. Fixed interval, no jitter, no ceiling -- every client that
# fails retries on the same 50ms cadence, so retries across clients stay
# synchronised and arrive at the backend in lockstep.
MAX_ATTEMPTS = 20
RETRY_INTERVAL_SECONDS = 0.05
