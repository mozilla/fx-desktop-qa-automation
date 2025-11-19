import pytest

from modules.browser_object import Navigation, TabBar
from modules.page_object_prefs import AboutPrefs

SEARCH_ENGINE = "DuckDuckGo"


@pytest.fixture()
def test_case():
    return "3028844"


def test_search_mode_cleared_on_engine_removal(driver):
    """
    C3028844 - Verify that removing a search engine from about:preferences#search clears search mode if that engine
    is currently selected in search mode in a different tab.
    """
    # Instantiate objects
    nav = Navigation(driver)
    tabs = TabBar(driver)
    prefs = AboutPrefs(driver, category="search")

    # Enter search mode for the desired search engine in a new tab
    nav.open_and_switch_to_new_window("tab")
    nav.open_usb_and_select_engine(SEARCH_ENGINE)

    # Verify search mode is entered for the corresponding engine
    nav.verify_search_mode_is_visible()

    # In another tab, remove that search engine from about:preferences#search
    nav.open_and_switch_to_new_window("tab")
    prefs.open()
    prefs.select_search_engine_from_tree(SEARCH_ENGINE)
    prefs.remove_search_engine(SEARCH_ENGINE)

    # Return to the first tab and verify search mode is cleared
    tabs.click_tab_by_index(1)
    nav.verify_search_mode_is_not_visible()
