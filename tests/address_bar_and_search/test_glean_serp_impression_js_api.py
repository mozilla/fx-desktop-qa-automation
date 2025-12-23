import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.classes.glean import GleanAsserts
from modules.page_object import AboutGlean, AboutPrefs
from modules.page_object_generics import GenericPage

# Test constants
SEARCH_ENGINE = "Ecosia"
SEARCH_TERM = "test"
GLEAN_METRIC = "serp.impression"

EXPECTED_PAYLOAD = {
    "provider": "ecosia",
    "source": "urlbar",
    "partner_code": "mzl",
    "tagged": "true",
}


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
    Test to verify Glean SERP impression data via Glean JS API.
    Uses Glean.serp.impression.testGetValue() instead of about:glean UI.
    """
    nav = Navigation(driver)
    prefs = AboutPrefs(driver, category="search")
    page = GenericPage(driver, url="about:newtab")
    glean = AboutGlean(driver)

    # Set search engine
    prefs.open()
    prefs.search_engine_dropdown().select_option(SEARCH_ENGINE)

    # Perform search
    page.open()
    nav.search(SEARCH_TERM)

    # Get events and assert
    events = glean.poll_glean_metric(GLEAN_METRIC)
    GleanAsserts.assert_payload(GLEAN_METRIC, events, EXPECTED_PAYLOAD)
