import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import AboutGlean, AboutPrefs
from modules.page_object_generics import GenericPage

# Test constants
SEARCH_TERM = "test"
SEARCH_ENGINE = "Ecosia"
GLEAN_METRIC_PATH = "serp.impression"

# Expected payload values
EXPECTED_PROVIDER = "ecosia"
EXPECTED_SOURCE = "urlbar"
EXPECTED_PARTNER_CODE = "mzl"


@pytest.fixture()
def test_case():
    return "GLEAN_SERP_TEST_JS_API"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.search.region", "DE"),
    ]


def test_glean_serp_impression_js_api(driver: Firefox):
    """
    Test to verify Glean SERP impression data via Glean JS API (browser console).
    Uses Glean.serp.impression.testGetValue() instead of about:glean UI.
    """
    nav = Navigation(driver)
    prefs = AboutPrefs(driver, category="search")
    glean = AboutGlean(driver)
    page = GenericPage(driver, url="about:newtab")

    # Set Ecosia as default search engine
    prefs.open()
    prefs.search_engine_dropdown().select_option(SEARCH_ENGINE)

    # Perform a search using the urlbar
    page.open()
    nav.search(SEARCH_TERM)

    # Poll Glean JS API until impression event is recorded (no UI needed)
    events = glean.poll_glean_metric(GLEAN_METRIC_PATH, timeout=15)
    assert len(events) > 0, "No serp.impression events recorded"

    # Get the newest event payload
    event = events[-1]
    payload = event.get("extra", {})

    # Assertions
    assert payload.get("provider") == EXPECTED_PROVIDER, payload
    assert payload.get("source") == EXPECTED_SOURCE, payload
    assert payload.get("partner_code") == EXPECTED_PARTNER_CODE, payload

    tagged = AboutGlean.normalize_glean_boolean(payload.get("tagged"))
    assert tagged is True, payload
