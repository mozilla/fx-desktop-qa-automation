import pytest
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_error_page import ErrorPage

KEYWORD = "google"
SEARCH_TERM = "firefox browser"
ENGINE_NAME = "Wikipedia"


@pytest.fixture()
def add_to_prefs_list():
    return [("keyword.enabled", False)]


@pytest.fixture()
def test_case():
    return "3028804"


def test_disable_websearch_from_awesome_bar(driver):
    """
    3028804 - Test that the websearch can be disabled from the preference but can be done via de USB
    """
    nav = Navigation(driver)
    tabs = TabBar(driver)
    error_page = ErrorPage(driver)

    # Enter "google" into the Awesome Bar
    nav.search(KEYWORD)

    # Wait for the tab title "Problem loading page"
    tabs.wait_for_tab_title("Problem loading page")

    # The Awesome Bar should still show exactly what was typed
    assert nav.get_awesome_bar_text() == KEYWORD

    # Firefox shows: "Server Not Found"
    assert "server not found" in error_page.get_error_title().lower()

    # Open a new tab and switch to it
    nav.open_and_switch_to_new_window("tab")

    # Select Wikipedia from USB
    nav.set_search_mode(ENGINE_NAME)

    # Perform a normal search
    nav.search(SEARCH_TERM)

    # Wait for Wikipedia page to load — use URL for reliability
    nav.title_contains("Wikipedia")
    nav.url_contains("wikipedia")
