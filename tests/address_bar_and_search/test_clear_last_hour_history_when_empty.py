import pytest
from selenium.webdriver import Firefox

from modules.util import PlacesHistory, Sanitizer

PROBE_URL = "https://example.com/history-test/never-visited"


@pytest.fixture()
def test_case():
    return "TODO-TESTRAIL-ID"


@pytest.fixture()
def add_to_prefs_list():
    return [("places.history.enabled", True)]


def test_clear_last_hour_history_when_empty(driver: Firefox):
    """
    Clearing the last hour of history succeeds when there is no
    history to clear.
    """
    # Instantiate objects
    history = PlacesHistory(driver)
    sanitizer = Sanitizer(driver)

    # Start from a known-empty history
    history.clear()

    # Clearing an empty range should be a no-op rather than an error
    cleared_range = sanitizer.sanitize(["history"], timespan="TIMESPAN_HOUR")
    assert cleared_range["start"] < cleared_range["end"], (
        f"Sanitizer reported a malformed clear range: {cleared_range}"
    )

    # Verify history is still empty
    presence = history.get_visit_presence([PROBE_URL])
    assert presence[PROBE_URL] is False, (
        f"Unexpected history entry after clearing empty history: {PROBE_URL}"
    )
