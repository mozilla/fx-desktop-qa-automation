import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_tabbar import TabBar


@pytest.fixture()
def test_case():
    return "3029196"


URL_FIXES = [
    ("cnn", "https://edition.cnn.com/"),
    ("facebook", "https://www.facebook.com/"),
]


@pytest.mark.parametrize("domain, expected_url", URL_FIXES)
def test_ctrl_enter_fixes_url(driver: Firefox, domain, expected_url: str):
    """
    C3029196 - Test that Ctrl/Cmd + Enter adds the entire url to a domain typed in the address bar.
    """

    # Instantiate objects
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Open a new tab
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()

    # Type a domain in the address bar and press Ctrl/Cmd + Enter
    nav.type_in_awesome_bar(domain)
    nav.press_ctrl_enter()

    # Verify navigation to the expected URL
    nav.url_contains(expected_url)
