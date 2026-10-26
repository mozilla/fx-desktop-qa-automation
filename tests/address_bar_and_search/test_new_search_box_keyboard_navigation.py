import pytest
from auto_fxui.browser_object import Navigation, TabBar
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

ENGINE = "Bing"
SEARCH_SETTINGS_URL = "about:preferences#search"


@pytest.fixture()
def test_case():
    return "3897535"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.search.widget.new", True)]


def test_new_search_box_keyboard_navigation(driver: Firefox):
    """
    C3897535 - The new search box widget can be accessed via keyboard operations only.
    """
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Setup: add the search bar to the toolbar.
    nav.add_search_bar_via_customizable_ui()

    # Step 1: Open a new tab and press Ctrl/Cmd+K.
    tabs.open_and_switch_to_new_tab()
    nav.perform_key_combo_chrome(Keys.CONTROL, "k")
    nav.verify_search_bar_is_focused()

    # Step 2: Shift+Tab to the search box widget.
    nav.perform_key_combo_chrome(Keys.SHIFT, Keys.TAB)
    nav.element_visible("searchbar-switcher-focused")

    # Step 3: Press Enter to open the dropdown.
    nav.perform_key_combo_chrome(Keys.ENTER)
    nav.element_visible("searchbar-switcher-popup")

    # Step 4: Move through the options with Down and Up.
    nav.press_down_until_focused("searchbar-switcher-option-focused", labels=[ENGINE])
    nav.perform_key_combo_chrome(Keys.UP)
    nav.element_not_visible("searchbar-switcher-option-focused", labels=[ENGINE])
    nav.press_down_until_focused("searchbar-switcher-prefs-focused")

    # Step 5: Press Enter on Search Settings.
    nav.perform_key_combo_chrome(Keys.ENTER)
    nav.url_contains(SEARCH_SETTINGS_URL)
