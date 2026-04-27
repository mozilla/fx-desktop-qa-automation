import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation


@pytest.fixture()
def test_case():
    return "3028887"


TAB_1_INPUT = "example"
TAB_1_EXPECTED_DOMAIN = "example.com"

TAB_2_INPUT = "facebook"
TAB_2_EXPECTED_DOMAIN = "facebook.com"


def test_ctrl_enter_refreshes_tab(driver: Firefox):
    """
    C3028887 - Verify that Ctrl/Cmd + R refreshes the webpage in the first tab
    after navigating with Ctrl/Cmd + Enter.
    """
    # Instantiate objects
    nav = Navigation(driver)

    # Open first tab and navigate using Ctrl+Enter
    nav.type_in_awesome_bar(TAB_1_INPUT)
    nav.perform_key_combo_chrome(Keys.CONTROL, Keys.ENTER)
    nav.url_contains(TAB_1_EXPECTED_DOMAIN)

    first_tab_url = driver.current_url

    # Open second tab and navigate using Ctrl+Enter
    nav.open_and_switch_to_new_window("tab")
    nav.type_in_awesome_bar(TAB_2_INPUT)
    nav.perform_key_combo_chrome(Keys.CONTROL, Keys.ENTER)
    nav.url_contains(TAB_2_EXPECTED_DOMAIN)

    # Switch back to first tab
    driver.switch_to.window(driver.window_handles[0])

    # Refresh using Ctrl/Cmd + R
    nav.refresh_page()

    # Verify successful reload (same URL)
    nav.url_contains(TAB_1_EXPECTED_DOMAIN)

    assert driver.current_url == first_tab_url
