"""
Decide whether the scheduled bug-test-links load should run today, and write
run=true or run=false to $GITHUB_OUTPUT.

Manual runs always go ahead. Scheduled runs (every Wednesday) go ahead every
second Wednesday from FIRST_RUN, and only after a major Firefox release in the
past RELEASE_WINDOW_DAYS. Uses only the standard library, so it needs no install.
"""

import json
import os
import urllib.request
from datetime import date

FIRST_RUN = date(2026, 11, 25)
RUN_EVERY_DAYS = 14
RELEASE_WINDOW_DAYS = 14
RELEASES_URL = (
    "https://product-details.mozilla.org/1.0/firefox_history_major_releases.json"
)


def is_run_day(today: date) -> bool:
    """True on FIRST_RUN and every RUN_EVERY_DAYS after it."""
    since_first = (today - FIRST_RUN).days
    return since_first >= 0 and since_first % RUN_EVERY_DAYS == 0


def released_recently(today: date, release_dates: list[date]) -> bool:
    """True if a major release shipped in the RELEASE_WINDOW_DAYS before today."""
    earlier = [day for day in release_dates if day < today]
    return bool(earlier) and (today - max(earlier)).days <= RELEASE_WINDOW_DAYS


def major_release_dates() -> list[date]:
    with urllib.request.urlopen(RELEASES_URL, timeout=60) as response:
        return [date.fromisoformat(day) for day in json.load(response).values()]


def should_run(event: str, today: date) -> bool:
    if event != "schedule":
        return True
    # skip alternate Wednesdays.
    if not is_run_day(today):
        print(f"{today}: not a fortnightly run day")
        return False
    run = released_recently(today, major_release_dates())
    print(f"{today}: {'a' if run else 'no'} major release in the past 14 days")
    return run


def main() -> int:
    run = should_run(os.environ.get("EVENT", ""), date.today())
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        print(f"run={str(run).lower()}", file=output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
