import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation, TabBar

DEFAULT_TERMS = ["mozilla", "firefox"]
OTHER_ENGINES = [("Bing", "bing.com"), ("DuckDuckGo", "duckduckgo.com")]
ENGINE_TERM = "browser"


@pytest.fixture()
def test_case():
    return "3897561"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.search.widget.new", True),
        ("sidebar.revamp", True),
        ("sidebar.verticalTabs", True),
    ]


def test_new_search_box_with_vertical_tabs(driver: Firefox):
    """
    C3897561 - New search box widget is functional with vertical tabs enabled.
    """
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Setup: add the search bar to the toolbar.
    nav.add_search_bar_via_customizable_ui()

    # Steps 1-2: Type a string in a new tab and search with the default engine.
    for term in DEFAULT_TERMS:
        tabs.open_and_switch_to_new_tab()
        nav.type_in_search_bar(term)
        nav.element_attribute_is("searchbar-input", "value", term)
        nav.type_in_search_bar(Keys.ENTER)
        nav.url_contains(term)

    # Step 3: Repeat with other engines.
    for engine, domain in OTHER_ENGINES:
        tabs.open_and_switch_to_new_tab()
        nav.type_in_search_bar(ENGINE_TERM)
        nav.element_attribute_is("searchbar-input", "value", ENGINE_TERM)
        nav.click_on("legacy-searchmode-switcher")
        nav.element_clickable("search-mode-switcher-option", labels=[engine])
        nav.js_click_on("search-mode-switcher-option", labels=[engine])
        nav.type_in_search_bar(Keys.ENTER)
        nav.url_contains(domain)
        nav.url_contains(ENGINE_TERM)
