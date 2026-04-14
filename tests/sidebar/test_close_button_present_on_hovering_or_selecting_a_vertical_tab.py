import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation, TabBar

URLS = ["about:robots", "about:logo", "about:mozilla", "about:blank"]
NUM_TABS = len(URLS)


@pytest.fixture()
def test_case():
    return "2652733"


def test_close_button_present_on_hovering_or_selecting_a_vertical_tab(driver: Firefox):
    """
    C2652733 - Verify the close (X) button is displayed and functional on a vertical tab when it is selected,
    hovered, or focused via keyboard.
    """
    tabs = TabBar(driver)
    nav = Navigation(driver)

    nav.toggle_vertical_tabs()
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    tabs.wait_for_num_tabs(NUM_TABS)

    # Select a vertical tab and verify its close button is visible and works.
    tab = tabs.get_tab(NUM_TABS)
    tabs.click_tab_by_index(NUM_TABS)
    tabs.expect_in_chrome(
        lambda d: tabs.get_element("tab-x-icon", parent_element=tab).is_displayed()
    )
    tabs.close_tab(tab)
    tabs.wait_for_num_tabs(NUM_TABS - 1)

    # Hover a vertical tab and verify its close button is visible and works.
    tab = tabs.get_tab(NUM_TABS - 1)
    tabs.hover(tab)
    tabs.expect_in_chrome(
        lambda d: tabs.get_element("tab-x-icon", parent_element=tab).is_displayed()
    )
    tabs.close_tab(tab)
    tabs.wait_for_num_tabs(NUM_TABS - 2)

    # Move focus into the vertical tab list with the keyboard, then move to the next tab.
    # Verify the focused tab shows the close button and can be closed.
    for _ in range(2):
        tabs.perform_key_combo_chrome(Keys.TAB)

    tabs.perform_key_combo_chrome(Keys.ARROW_DOWN)

    tab = tabs.get_tab(2)
    tabs.expect_in_chrome(
        lambda d: tabs.get_element("tab-x-icon", parent_element=tab).is_displayed()
    )
    tabs.close_tab(tab)
    tabs.wait_for_num_tabs(NUM_TABS - 3)
