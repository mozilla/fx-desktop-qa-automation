import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from auto_fxui.browser_object import Navigation, TabBar
from auto_fxui.page_object import AboutPrefs

SEARCH_TERM = "mozilla"


@pytest.fixture()
def test_case():
    return "3897530"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.search.widget.new", True)]


def test_new_search_box_suggestions_disabled(driver: Firefox):
    """
    C3897530 - Search suggestions are not in the search box when turned off.
    """
    nav = Navigation(driver)
    tabs = TabBar(driver)
    prefs = AboutPrefs(driver, category="search")

    # Setup: add the search bar to the toolbar.
    nav.add_search_bar_via_customizable_ui()

    # Step 1: Turn off search suggestions.
    prefs.open()
    prefs.select_search_suggestions_in_address_bar(False)

    # Step 2: Open a new tab and focus the search box.
    tabs.open_and_switch_to_new_tab()
    nav.click_on("searchbar-input")
    nav.verify_search_bar_is_focused()

    # Step 3: Type a string; no suggestions show up.
    nav.verify_no_external_suggestions(SEARCH_TERM, "search")

    # Step 4: Submit the search.
    nav.type_in_search_bar(Keys.ENTER)
    nav.url_contains(SEARCH_TERM)
