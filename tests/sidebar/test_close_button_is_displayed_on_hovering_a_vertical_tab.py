import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation, TabBar

URLS = ["about:robots", "about:logo", "about:mozilla", "about:blank"]
NUM_TABS = 4


@pytest.fixture()
def test_case():
    return "2652733"


def test_close_button_is_displayed_on_hovering_a_vertical_tab(driver: Firefox):
    """
    C2652733 - Verify the close (X) button is displayed and functional on a vertical tab when it is selected,
    hovered, or focused via keyboard.
    """
    # Instantiate objects
    tabs = TabBar(driver)
    nav = Navigation(driver)

    # Open the sidebar with a few vertical tabs
    nav.toggle_vertical_tabs()
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    tabs.wait_for_num_tabs(NUM_TABS)

    # Select a vertical tab - close button is displayed, close the tab
    tab = tabs.get_tab(NUM_TABS)
    tabs.click_tab_by_index(NUM_TABS)
    tabs.close_tab(tab)
    tabs.wait_for_num_tabs(NUM_TABS - 1)

    # Hover over a vertical tab - close button is displayed, close the tab
    tab = tabs.get_tab(NUM_TABS - 1)
    tabs.hover(tab)
    tabs.close_tab(tab)
    tabs.wait_for_num_tabs(NUM_TABS - 2)

    # Focus a vertical tab using the keyboard — close button is displayed, close the tab
    tabs.click_tab_by_index(1)
    tabs.perform_key_combo_chrome(Keys.ARROW_DOWN)
    tab = tabs.get_tab(2)
    tabs.close_tab(tab)
    tabs.wait_for_num_tabs(NUM_TABS - 3)
