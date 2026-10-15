import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation

DEFAULT_TERMS = ["mozilla", "firefox"]
OTHER_ENGINES = [("Bing", "bing.com"), ("DuckDuckGo", "duckduckgo.com")]
ENGINE_TERM = "browser"


@pytest.fixture()
def test_case():
    return "3897563"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.search.widget.new", True)]


def test_new_search_box_searches_in_private_window(driver: Firefox):
    """
    C3897563 - Searches are performed correctly with the new search box in PBM.
    """
    nav = Navigation(driver)

    # Setup: add the search bar to the toolbar.
    nav.add_search_bar_via_customizable_ui()

    # Step 1: Open a private window and focus the search box.
    nav.open_and_switch_to_private_window_via_keyboard()
    nav.click_on("searchbar-input")
    nav.verify_search_bar_is_focused()

    # Step 2: Search a few times with the default engine.
    for term in DEFAULT_TERMS:
        nav.clear_search_bar()
        nav.search_bar_search(term)
        nav.url_contains(term)

    # Step 3: Search with other engines using search mode.
    for engine, domain in OTHER_ENGINES:
        nav.clear_search_bar()
        nav.click_on("legacy-searchmode-switcher")
        nav.element_clickable("search-mode-switcher-option", labels=[engine])
        nav.js_click_on("search-mode-switcher-option", labels=[engine])
        nav.type_in_search_bar(ENGINE_TERM + Keys.ENTER)
        nav.url_contains(domain)
        nav.url_contains(ENGINE_TERM)
