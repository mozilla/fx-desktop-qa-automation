from datetime import datetime, timedelta, timezone

import pytest
from selenium.webdriver import Firefox

from modules.util import PlacesHistory, Sanitizer


@pytest.fixture()
def test_case():
    return "2058317"


@pytest.fixture()
def add_to_prefs_list():
    return [("places.history.enabled", True)]


RECENT_URLS = {
    "https://example.com/history-test/recent-10-minutes": timedelta(minutes=10),
    "https://example.com/history-test/recent-55-minutes": timedelta(minutes=55),
}
OLD_URLS = {
    "https://example.com/history-test/old-65-minutes": timedelta(minutes=65),
    "https://example.com/history-test/old-2-hours": timedelta(hours=2),
}


def test_clear_last_hour_history(driver: Firefox):
    """
    Clearing the last hour of history removes visits from within that
    hour and preserves older ones.
    """
    # Instantiate objects
    history = PlacesHistory(driver)
    sanitizer = Sanitizer(driver)

    # Start from a known-empty history so nothing from browser startup counts
    history.clear()

    # Arrange visits on both sides of the one-hour boundary
    now = datetime.now(timezone.utc)
    visits = [
        {
            "url": url,
            "title": f"History test visit - {url.rsplit('/', 1)[-1]}",
            "timestamp_ms": PlacesHistory.to_epoch_ms(now - offset),
        }
        for url, offset in {**RECENT_URLS, **OLD_URLS}.items()
    ]
    history.insert_visits(visits)

    # Precondition: every arranged visit is present before anything is cleared
    presence_before = history.get_visit_presence([visit["url"] for visit in visits])
    assert all(presence_before.values()), (
        f"Not all test visits were recorded: {presence_before}"
    )

    # Clear only browsing history, only for the last hour
    cleared_range = sanitizer.sanitize(["history"], timespan="TIMESPAN_HOUR")
    assert cleared_range["start"] < cleared_range["end"], (
        f"Sanitizer reported a malformed clear range: {cleared_range}"
    )

    # Verify visits inside the last hour are gone and older ones survived
    presence_after = history.get_visit_presence([visit["url"] for visit in visits])
    for url in RECENT_URLS:
        assert presence_after[url] is False, (
            f"Visit from within the last hour was not removed: {url}"
        )
    for url in OLD_URLS:
        assert presence_after[url] is True, (
            f"Visit from before the last hour was incorrectly removed: {url}"
        )
