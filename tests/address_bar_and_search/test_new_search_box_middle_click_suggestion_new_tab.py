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
    return "3897538"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.search.widget.new", True),
        ("browser.search.suggest.enabled", True),
    ]


def test_new_search_box_middle_click_suggestion_new_tab(driver: Firefox):
    """C3897538 - Middle click on search suggestions opens them in new tabs."""
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Setup: add the search bar to the toolbar.
    nav.add_search_bar_via_customizable_ui()

    # Step 1: Type a string that gives suggestions.
    nav.type_in_search_bar(FIRST_TERM)

    # Step 2: Middle click a suggestion; the SERP opens in a new foreground tab.
    nav.middle_click_search_bar_suggestion()
    tabs.wait_for_num_tabs(2)
    tabs.element_attribute_is("tab-by-index", "selected", "true", labels=["2"])
    tabs.switch_to_new_tab()
    nav.url_contains(DEFAULT_ENGINE_DOMAIN)
    nav.url_contains(FIRST_TERM)

    # Step 3: Enter Bing search mode and middle click a suggestion.
    nav.click_on("legacy-searchmode-switcher")
    # A normal click can't reach menu items, so wait for it and use a JS click.
    nav.element_clickable("search-mode-switcher-option", labels=[ENGINE])
    nav.js_click_on("search-mode-switcher-option", labels=[ENGINE])
    nav.element_attribute_contains(
        "legacy-searchmode-switcher-button", "aria-label", ENGINE
    )
    nav.clear_search_bar()
    nav.type_in_search_bar(SECOND_TERM)
    nav.middle_click_search_bar_suggestion()

    # The Bing SERP opens in another new foreground tab.
    tabs.wait_for_num_tabs(3)
    tabs.element_attribute_is("tab-by-index", "selected", "true", labels=["3"])
    tabs.switch_to_new_tab()
    nav.url_contains(ENGINE_DOMAIN)
    nav.url_contains(SECOND_TERM)
