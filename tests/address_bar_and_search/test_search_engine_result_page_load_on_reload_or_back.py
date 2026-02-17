import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_about_pages import AboutTelemetry
from modules.util import Utilities

TEXT = "Firefox"
SEARCHBAR_PATH = (
    '$..["browser.search.content.searchbar"].["google:tagged:firefox-b-1-d"]'
)


@pytest.fixture()
def test_case():
    return "3028909"


def test_search_engine_result_page_load_on_reload_or_back(driver: Firefox):
    """
    C3028909 - Search Engine Result Page loads as a result of a reload or a back-button press
    """

    # Instantiate objects
    nav = Navigation(driver)
    telemetry = AboutTelemetry(driver)
    utils = Utilities()
    tab = TabBar(driver)

    # Go to "Customize Toolbar", drag Search bar to Toolbar and click Done
    nav.add_search_bar_to_toolbar()

    # Using the search bar perform a search
    nav.search_bar_search(TEXT)
    nav.url_contains(TEXT)

    # Press back button from the browser menu
    nav.click_back_button()
    nav.wait.until(lambda _: TEXT not in nav.driver.current_url)

    # Go to about:telemetry -> Raw JSON -> Raw data
    telemetry.open()
    telemetry.open_raw_json_data()

    # Verify "browser.search.content.searchbar": { "google:tagged:firefox-b-d": 1}*
    json_data = utils.decode_url(driver)
    searchbar_ping = utils.assert_json_value(json_data, SEARCHBAR_PATH, 1)
    assert searchbar_ping, f"Telemetry path not found: {SEARCHBAR_PATH}"

    # Open new tab and perform a new search in the search bar
    tab.new_tab_by_button()
    nav.search_bar_search(TEXT)

    # Press reload button
    nav.refresh_page()

    # Go back to raw data page and reload it
    driver.switch_to.window(driver.window_handles[1])
    nav.refresh_page()
    telemetry.click_on("rawdata-tab")

    # Verify "browser.search.content.searchbar": { "google:tagged:firefox-b-d": 2}*
    json_data = utils.decode_url(driver)
    ping_value = utils.assert_json_value(json_data, SEARCHBAR_PATH, 2)
    assert ping_value, f"Telemetry path not found or value mismatch: {SEARCHBAR_PATH}"
