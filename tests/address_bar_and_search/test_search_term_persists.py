import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TabBar
from modules.page_object import AboutPrefs
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "3029211"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.urlbar.showSearchTerms.enabled", True),
        ("browser.urlbar.showSearchTerms.featureGate", True),
    ]


SEARCH_ENGINE = "DuckDuckGo"
FIRST_SEARCH = "cheetah"
SECOND_SEARCH = "lion"


def test_search_term_persists(driver: Firefox):
    """
    C2153943 - Persist search term basic functionality
    """

    nav = Navigation(driver)
    tab = TabBar(driver)
    prefs = AboutPrefs(driver, category="search")
    page = GenericPage(driver, url="about:blank")

    prefs.open()
    prefs.select_default_search_engine_by_key(SEARCH_ENGINE)

    nav.search(FIRST_SEARCH)
    # Wait for the SERP to actually render results before asserting; the "show
    # search terms" feature swaps the SERP URL in the urlbar for the search term
    # asynchronously, so gate on real SERP content rather than reading once.
    page.element_visible("duckduckgo-search-result")
    tab.expect_title_contains(SEARCH_ENGINE)
    nav.element_attribute_is("awesome-bar", "value", FIRST_SEARCH)

    nav.set_content_context()
    driver.get("about:robots")

    nav.search(SECOND_SEARCH)
    page.element_visible("duckduckgo-search-result")
    tab.expect_title_contains(SEARCH_ENGINE)
    nav.element_attribute_is("awesome-bar", "value", SECOND_SEARCH)
