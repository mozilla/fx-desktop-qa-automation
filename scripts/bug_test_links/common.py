"""Settings and HTTP helpers shared by the bug-test-links loader."""

import os
from datetime import datetime, timezone
from time import sleep
from typing import Any

import requests

SINCE_DATE = os.environ.get("SINCE_DATE") or "2026-10-13"
HEADERS = {"User-Agent": "starfox-bug-test-links"}


def since_epoch() -> int:
    return int(
        datetime.fromisoformat(SINCE_DATE).replace(tzinfo=timezone.utc).timestamp()
    )


def epoch_to_iso(value: int | None) -> str | None:
    return datetime.fromtimestamp(value, timezone.utc).isoformat() if value else None


def get_json(url: str, params: dict, retries: int = 5) -> Any:
    """GET with a wait-and-retry on rate limiting."""
    for attempt in range(retries):
        response = requests.get(url, params=params, headers=HEADERS, timeout=120)
        if response.status_code != 429 or attempt == retries - 1:
            response.raise_for_status()
            return response.json()
        sleep(int(response.headers.get("Retry-After", 60)))
