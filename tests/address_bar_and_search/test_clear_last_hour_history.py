from datetime import datetime, timedelta, timezone

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.page_object import GenericPage
from modules.util import PlacesHistory, Sanitizer

# Offsets are kept 5 minutes clear of the one-hour boundary on both sides, so
# the seconds that elapse between arranging the visits and clearing cannot
# drift a visit across the cutoff.
RECENT_URLS = {
    "https://example.com/history-test/recent-10-minutes": timedelta(minutes=10),
    "https://example.com/history-test/recent-55-minutes": timedelta(minutes=55),
}
OLD_URLS = {
    "https://example.com/history-test/old-65-minutes": timedelta(minutes=65),
    "https://example.com/history-test/old-2-hours": timedelta(hours=2),
}


@pytest.fixture()
def test_case():
    return "4245709"


@pytest.fixture()
def add_to_prefs_list():
    return [("places.history.enabled", True)]


def arrange_visits_across_the_boundary(history: PlacesHistory) -> list:
    """
    Reset history and seed visits on both sides of the one-hour boundary.

    Visits are written through Places because no automated route can browse an
    hour ago. Returns the arranged visit dicts.
    """
    history.clear()
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
    return visits


def assert_only_the_last_hour_was_cleared(history: PlacesHistory, visits: list):
    """Recent visits must be gone, older ones must remain."""
    presence_after = history.get_visit_presence([visit["url"] for visit in visits])
    for url in RECENT_URLS:
        assert presence_after[url] is False, (
            f"Visit from within the last hour was not removed: {url}"
        )
    for url in OLD_URLS:
        assert presence_after[url] is True, (
            f"Visit from before the last hour was incorrectly removed: {url}"
        )


def test_clear_last_hour_history(driver: Firefox):
    """
    Clearing the last hour of history removes visits from within that
    hour and preserves older ones.
    """
    # Instantiate objects
    history = PlacesHistory(driver)
    sanitizer = Sanitizer(driver)

    visits = arrange_visits_across_the_boundary(history)

    # Clear only browsing history, only for the last hour
    cleared_range = sanitizer.sanitize(["history"], timespan="TIMESPAN_HOUR")
    assert cleared_range["start"] < cleared_range["end"], (
        f"Sanitizer reported a malformed clear range: {cleared_range}"
    )

    assert_only_the_last_hour_was_cleared(history, visits)


def test_clear_last_hour_history_ui(driver: Firefox):
    """
    Clearing Last hour from the Clear browsing data and cookies dialog removes
    visits from within that hour and preserves older ones.
    """
    # Instantiate objects
    history = PlacesHistory(driver)
    panel = PanelUi(driver)
    page = GenericPage(driver)

    visits = arrange_visits_across_the_boundary(history)

    # Open Clear browsing data and cookies from the hamburger menu
    panel.open_history_menu()
    panel.open_clear_history_dialog()

    # Choose the one-hour range and clear browsing history alone. Last hour is
    # already the dialog default, so the range is asserted rather than assumed
    # to have been set by the click.
    panel.select_history_time_range_option("Last hour")
    # Each of these is read once and held, so the failure message reports the
    # state that actually failed rather than whatever a second read returns.
    time_range = panel.get_clear_history_time_range()
    assert time_range == "Last hour", (
        f"Expected the time range dropdown to show Last hour, got {time_range!r}"
    )

    panel.set_clear_history_categories(["browsingHistoryAndDownloads"])
    checked = panel.get_clear_history_categories_checked()
    assert checked == ["browsingHistoryAndDownloads"], (
        f"Expected browsing history to be the only ticked category, got {checked}"
    )

    page.click_on("clear-history-button")

    assert_only_the_last_hour_was_cleared(history, visits)
