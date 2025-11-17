import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar

TEST_WEBSITE = "https://www.firefox.com/"


@pytest.fixture()
def test_case():
    return "3028997"


def test_verify_url_after_tab_switch_with_search_mode(driver: Firefox):
    """
    C3028842: URL is correctly displayed after switching tab with search mode opened
    """

    # Instantiate objects
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Open a new tab, open any website
    nav.search(TEST_WEBSITE)

    # Open another new tab and click History from the USB
    tabs.new_tab_by_button()
    nav.click_search_mode_switcher()
    nav.click_history_button_search_mode()

    # Click the earlier opened tab
    tabs.click_tab_by_index(1)

    # Check previous tab is opened and url string is correctly displayed
    nav.url_contains(TEST_WEBSITE)
