import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation, TabBar

ENGINE = "Bing"
ENGINE_DOMAIN = "bing.com"
SEARCH_TERM = "mozilla"


@pytest.fixture()
def test_case():
    return "3897536"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.search.widget.new", True)]


def test_new_search_box_keyboard_search(driver: Firefox):
    """
    C3897536 - Searches can be submitted via keyboard operations only.
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

    # Step 4: Pick an engine with Down and press Enter to enter search mode.
    nav.press_down_until_focused("searchbar-switcher-option-focused", labels=[ENGINE])
    nav.perform_key_combo_chrome(Keys.ENTER)
    nav.element_attribute_contains(
        "legacy-searchmode-switcher-button", "aria-label", ENGINE
    )

    # Step 5: Type a string and press Enter to search.
    nav.verify_search_bar_is_focused()
    nav.perform_key_combo_chrome(SEARCH_TERM)
    nav.perform_key_combo_chrome(Keys.ENTER)
    nav.url_contains(ENGINE_DOMAIN)
    nav.url_contains(SEARCH_TERM)
