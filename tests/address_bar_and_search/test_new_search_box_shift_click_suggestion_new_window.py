import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TabBar

DEFAULT_ENGINE_DOMAIN = "google.com"
ENGINE = "Bing"
ENGINE_DOMAIN = "bing.com"
FIRST_TERM = "mozilla"
SECOND_TERM = "firefox"


@pytest.fixture()
def test_case():
    return "3897575"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.search.widget.new", True)]


def test_new_search_box_shift_click_suggestion_new_window(driver: Firefox):
    """C3897575 - Shift + Click opens the search in a new window."""
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Setup: add the search bar to the toolbar.
    nav.add_search_bar_via_customizable_ui()

    # Step 1: Type a string that gives suggestions.
    nav.type_in_search_bar(FIRST_TERM)
    nav.verify_search_bar_is_focused()

    # Step 2: Shift + Click a suggestion; the default engine SERP opens in a new window.
    nav.shift_click_search_bar_suggestion()
    tabs.wait_for_num_windows(2)
    tabs.switch_to_new_window()
    nav.url_contains(DEFAULT_ENGINE_DOMAIN)
    nav.url_contains(FIRST_TERM)

    # Step 3: Enter Bing search mode and Shift + Click a suggestion.
    nav.click_on("legacy-searchmode-switcher")
    # A normal click can't reach menu items, so wait for it and use a JS click.
    nav.element_clickable("search-mode-switcher-option", labels=[ENGINE])
    nav.js_click_on("search-mode-switcher-option", labels=[ENGINE])
    nav.element_attribute_contains(
        "legacy-searchmode-switcher-button", "aria-label", ENGINE
    )
    nav.type_in_search_bar(SECOND_TERM)
    nav.shift_click_search_bar_suggestion()

    # The Bing SERP opens in another new window.
    tabs.wait_for_num_windows(3)
    tabs.switch_to_new_window()
    nav.url_contains(ENGINE_DOMAIN)
    nav.url_contains(SECOND_TERM)
