import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_about_pages import AboutTelemetry
from modules.util import Utilities

TEXT = "Firefox"
SEARCHBAR_PATH = (
    '$..["browser.search.content.searchbar"].["google:tagged:firefox-b-1-d"]'
)


@pytest.fixture()
def test_case():
    return "3028909"


def test_search_engine_result_page_load_on_reload(driver: Firefox):
    """
    C3028909 - Search Engine Result Page loads as a result of a reload
    """

    # Instantiate objects
    nav = Navigation(driver)
    telemetry = AboutTelemetry(driver)
    utils = Utilities()

    # Go to "Customize Toolbar", drag Search bar to Toolbar and click Done
    nav.add_search_bar_to_toolbar()

    # Using the search bar perform a search
    nav.search_bar_search(TEXT)
    nav.url_contains(TEXT)
    nav.refresh_page()

    # Go to about:telemetry -> Raw JSON -> Raw data
    telemetry.open()
    telemetry.open_raw_json_data()

    # Verify "browser.search.content.searchbar": { "google:tagged:firefox-b-d": 1}*
    json_data = utils.decode_url(driver)
    searchbar_ping = utils.assert_json_value(json_data, SEARCHBAR_PATH, 1)
    assert searchbar_ping, f"Telemetry path not found: {SEARCHBAR_PATH}"
