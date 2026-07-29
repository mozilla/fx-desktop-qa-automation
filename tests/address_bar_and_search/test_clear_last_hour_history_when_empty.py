import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.page_object import GenericPage
from modules.util import PlacesHistory, Sanitizer


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
    assert history.is_history_empty(), "History was not empty to begin with"

    # Clearing an empty range should be a no-op rather than an error
    cleared_range = sanitizer.sanitize(["history"], timespan="TIMESPAN_HOUR")
    assert cleared_range["start"] < cleared_range["end"], (
        f"Sanitizer reported a malformed clear range: {cleared_range}"
    )

    # The point of the test is that the call above did not raise. This confirms
    # it was a genuine no-op rather than something that left visits behind.
    assert history.is_history_empty(), (
        "History is not empty after clearing an already-empty history"
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
    assert history.is_history_empty(), "History was not empty to begin with"

    # Open Clear browsing data and cookies from the hamburger menu
    panel.open_history_menu()
    panel.open_clear_history_dialog()

    # Choose the one-hour range and clear browsing history alone
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

    # Clearing nothing should be a no-op rather than an error
    page.click_on("clear-history-button")
    panel.wait_for_clear_history_dialog_closed()

    # The point of the test is that the dialog flow above completed without
    # raising. This confirms it left history empty rather than adding entries.
    assert history.is_history_empty(), (
        "History is not empty after clearing an already-empty history"
    )
