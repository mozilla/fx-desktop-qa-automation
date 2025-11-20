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
    nav = Navigation(driver)
    tabs = TabBar(driver)
    error_page = ErrorPage(driver)

    # Enter "google" into the Awesome Bar
    nav.search(KEYWORD)

    # Wait for the tab title "Server Not Found"
    tabs.wait_for_tab_title("Server Not Found")

    # The Awesome Bar should still show exactly what was typed
    assert nav.get_awesome_bar_text() == KEYWORD

    # Firefox 138+ shows: "Hmm. We’re having trouble finding that site."
    assert "having trouble finding that site" in error_page.get_error_title().lower()

    # Open a new tab and switch to it
    nav.open_and_switch_to_new_window("tab")

    # Select Wikipedia from USB
    nav.open_usb_and_select_option(ENGINE_NAME)

    # Perform a normal search
    nav.search(SEARCH_TERM)

    # Wait for Wikipedia page to load — using driver.title for reliability
    wait = WebDriverWait(driver, 10)
    wait.until(lambda d: "wikipedia" in d.title.lower())

    # Address bar contains "wikipedia"
    assert "wikipedia" in nav.get_awesome_bar_text().lower()
