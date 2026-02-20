import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar

TEST_WEBSITE = "https://www.firefox.com/"
OPTION = "History"
TAB_TITLE = "Get Firefox for desktop — Firefox (US)"


@pytest.fixture()
def test_case():
    return "3028842"


def test_verify_url_after_tab_switch_with_search_mode(driver: Firefox):
    """
    C3028842: URL is correctly displayed after switching tab with search mode opened
    """

    # Instantiate objects
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Open any website
    nav.search(TEST_WEBSITE)
    tabs.wait_for_tab_title(TAB_TITLE)

    # Open another new tab and click History from the USB
    tabs.new_tab_by_button()
    nav.open_usb_and_select_option(OPTION)

    # Click the earlier opened tab
    tabs.click_tab_by_index(1)

    # Check previous tab is opened and url string is correctly displayed
    nav.url_contains(TEST_WEBSITE)
