import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation, TabBar

FIRST_TERM = "mozilla"
SECOND_TERM = "firefox"


@pytest.fixture()
def test_case():
    return "3897528"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.search.widget.new", True)]


def test_new_search_box_searches(driver: Firefox):
    """
    C3897528 - Searches are performed correctly with the new search box.
    """
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Setup: add the search bar to the toolbar.
    nav.add_search_bar_via_customizable_ui()

    # Step 1: Type a string in the search box in a new tab.
    tabs.open_and_switch_to_new_tab()
    nav.type_in_search_bar(FIRST_TERM)
    nav.element_attribute_is("searchbar-input", "value", FIRST_TERM)

    # Step 2: Submit with the go arrow.
    nav.click_on("searchbar-go-button")
    nav.url_contains(FIRST_TERM)

    # Step 3: Type a string in the search box in a new tab.
    tabs.open_and_switch_to_new_tab()
    nav.type_in_search_bar(SECOND_TERM)
    nav.element_attribute_is("searchbar-input", "value", SECOND_TERM)

    # Step 4: Submit with Enter; the string stays in the search box.
    nav.type_in_search_bar(Keys.ENTER)
    nav.url_contains(SECOND_TERM)
    nav.element_attribute_is("searchbar-input", "value", SECOND_TERM)
