from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TabBar
from modules.page_object import AboutGlean, AboutPrefs

# Test constants
SEARCH_TERM = "test"
SEARCH_ENGINE = "Ecosia"
METRIC_NAME = "serp.impression"
METRIC_FILTER = "serp"

# Expected payload values
EXPECTED_PROVIDER = "ecosia"
EXPECTED_SOURCE = "urlbar"
EXPECTED_PARTNER_CODE = "mzl"


@pytest.fixture()
def test_case():
    return "GLEAN_SERP_TEST"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.search.region", "DE"),
    ]


def test_glean_serp_impression(driver: Firefox):
    """
    Test to verify Glean SERP impression data via about:glean.
    """
    nav = Navigation(driver)
    prefs = AboutPrefs(driver, category="search")
    tabs = TabBar(driver)
    glean = AboutGlean(driver)

    # Set Ecosia as default search engine
    prefs.open()
    prefs.search_engine_dropdown().select_option(SEARCH_ENGINE)

    # Perform a search using the urlbar
    driver.get("about:newtab")
    nav.search(SEARCH_TERM)

    # Buffer for telemetry event to be recorded before opening about:glean
    sleep(2)

    # Open about:glean in a new tab
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    glean.open()

    # Enable Metrics Table and filter to serp
    glean.enable_metrics_table()
    glean.filter_metrics(METRIC_FILTER)
    glean.load_metric(METRIC_NAME)

    # Select newest event and verify payload
    glean.click_newest_metric_event(METRIC_NAME)
    payload = glean.get_metric_payload(METRIC_NAME)

    # Assertions
    assert payload.get("provider") == EXPECTED_PROVIDER, payload
    assert payload.get("source") == EXPECTED_SOURCE, payload
    assert payload.get("partner_code") == EXPECTED_PARTNER_CODE, payload

    tagged = AboutGlean.normalize_glean_boolean(payload.get("tagged"))
    assert tagged is True, payload
