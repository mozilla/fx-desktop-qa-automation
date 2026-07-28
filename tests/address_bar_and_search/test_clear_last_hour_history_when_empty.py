import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.page_object import GenericPage
from modules.util import PlacesHistory, Sanitizer

PROBE_URL = "https://example.com/history-test/never-visited"


@pytest.fixture()
def test_case():
    return "4245710"


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


def test_clear_last_hour_history_when_empty_ui(driver: Firefox):
    """
    Clearing Last hour from the Clear browsing data and cookies dialog succeeds
    when there is no history to clear.
    """
    # Instantiate objects
    history = PlacesHistory(driver)
    panel = PanelUi(driver)
    page = GenericPage(driver)

    # Start from a known-empty history
    history.clear()

    # Open Clear browsing data and cookies from the hamburger menu
    panel.open_history_menu()
    panel.open_clear_history_dialog()

    # Choose the one-hour range and clear browsing history alone
    panel.select_history_time_range_option("Last hour")
    assert panel.get_clear_history_time_range() == "Last hour", (
        "Time range dropdown does not show Last hour"
    )

    panel.set_clear_history_categories(["browsingHistoryAndDownloads"])
    assert panel.get_clear_history_categories_checked() == [
        "browsingHistoryAndDownloads"
    ], (
        "Expected browsing history to be the only ticked category, got "
        f"{panel.get_clear_history_categories_checked()}"
    )

    # Clearing nothing should be a no-op rather than an error
    page.click_on("clear-history-button")

    # Verify history is still empty
    presence = history.get_visit_presence([PROBE_URL])
    assert presence[PROBE_URL] is False, (
        f"Unexpected history entry after clearing empty history: {PROBE_URL}"
    )
