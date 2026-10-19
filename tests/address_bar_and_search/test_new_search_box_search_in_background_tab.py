import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation, TabBar

SEARCH_TERM = "mozilla"


@pytest.fixture()
def test_case():
    return "3897537"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.search.widget.new", True)]


def test_new_search_box_search_in_background_tab(driver: Firefox):
    """
    C3897537 - Alt / Option + Shift + Enter performs the search in a background tab.
    """
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Setup: add the search bar to the toolbar.
    nav.add_search_bar_via_customizable_ui()

    # Step 1: Open a new tab and press Ctrl/Cmd + K.
    tabs.open_and_switch_to_new_tab()
    nav.perform_key_combo_chrome(Keys.CONTROL, "k")
    nav.verify_search_bar_is_focused()

    # Step 2: Type a term and press Alt/Option + Shift + Enter.
    nav.type_in_search_bar(SEARCH_TERM)
    nav.perform_key_combo_chrome(Keys.ALT, Keys.SHIFT, Keys.ENTER)

    # The SERP opens in a third tab, but the second tab stays selected.
    tabs.wait_for_num_tabs(3)
    tabs.element_attribute_is("tab-by-index", "selected", "true", labels=["2"])
    tabs.element_attribute_is_not("tab-by-index", "selected", "true", labels=["3"])

    # The search box keeps the term.
    nav.element_attribute_is("searchbar-input", "value", SEARCH_TERM)

    # The background tab has the SERP.
    tabs.switch_to_new_tab()
    nav.url_contains(SEARCH_TERM)
