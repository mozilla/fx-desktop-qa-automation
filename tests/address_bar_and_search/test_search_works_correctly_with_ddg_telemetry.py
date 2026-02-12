import time

import pytest
from selenium.webdriver.common.by import By

from modules.browser_object import Navigation
from modules.page_object_about_pages import AboutTelemetry
from modules.util import Utilities
from tests.preferences.test_clear_cookie_data import WEBSITE_ADDRESS

SEARCH_TERM = "buy stocks"
SEARCH_TERM2 = "mozilla wikipedia"
SEARCH_ENGINE = "DuckDuckGo"


@pytest.fixture()
def test_case():
    return "3029250"


def test_search_works_correctly_with_ddg_telemetry(driver):
    nav = Navigation(driver)
    telemetry = AboutTelemetry(driver)
    util = Utilities()

    # Step 1: Go to the website and select DuckDuckGo as a search engine
    driver.get(WEBSITE_ADDRESS)
    nav.click_search_mode_switcher()
    nav.set_search_mode(SEARCH_ENGINE)

    # Step 2: Perform the search
    nav.clear_awesome_bar()
    nav.search(SEARCH_TERM)
    time.sleep(1)  # Wait for search to complete and telemetry to record

    # Step 3: Open a new tab and go to telemetry and verify search term is recorded
    telemetry.open()
    time.sleep(2)  # Wait for telemetry to load
    telemetry.open_raw_json_data()

    # Decode telemetry JSON
    json_data = util.decode_url(driver)

    assert util.assert_json_value(
        json_data,
        '$..["ddg.urlbar-searchmode"].["bucket_count"]',
        3,
    )

    assert util.assert_json_value(
        json_data,
        '$..["ddg.urlbar-searchmode"].["histogram_type"]',
        4,
    )

    assert util.assert_json_value(
        json_data,
        '$..["ddg.urlbar-searchmode"].["sum"]',
        1,
    )

    assert util.assert_json_value(
        json_data,
        '$..["ddg.urlbar-searchmode"].["range"]',
        [1, 2],
    )

    # Step 4: Go back to the search engine, perform another search, click on the first result, and go back
    driver.get("about:newtab")
    nav.clear_awesome_bar()
    nav.click_search_mode_switcher()
    nav.set_search_mode(SEARCH_ENGINE)
    nav.search(SEARCH_TERM2)
    time.sleep(1)
    # Click on the first search result. No need to save this object
    results = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="result-title-a"]')
    results[0].click()
    nav.click_back_button()
    time.sleep(1)  # Wait for navigation to complete

    # Step 5: Go back to telemetry and verify tabhistory is recorded
    # Re-open telemetry after content interaction
    telemetry.open()
    nav.switch_to_new_tab()
    time.sleep(1)  # Wait for telemetry to load

    telemetry = AboutTelemetry(driver)
    telemetry.open_raw_json_data()
    time.sleep(1)  # Wait for raw data to load

    # Decode telemetry JSON again
    json_data = util.decode_url(driver)

    # --- browser.search.content.tabhistory ---
    assert util.assert_json_value(
        json_data,
        '$..["browser.search.content.tabhistory"].["duckduckgo:tagged:ffab"]',
        1,
    ), "Missing or incorrect browser.search.content.tabhistory ping"
