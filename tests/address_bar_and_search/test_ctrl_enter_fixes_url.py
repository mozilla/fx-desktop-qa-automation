import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation


@pytest.fixture()
def test_case():
    return "3029196"


URL_FIXES = [
    ("example", "https://www.example.com/"),
    ("facebook", "https://www.facebook.com/"),
]


@pytest.mark.parametrize("domain, expected_url", URL_FIXES)
def test_ctrl_enter_fixes_url(driver: Firefox, domain, expected_url: str):
    """
    C3029196 - Test that Ctrl/Cmd + Enter adds the entire url to a domain typed in the address bar.
    """

    # Instantiate objects
    nav = Navigation(driver)

    # Open a new tab
    nav.open_and_switch_to_new_window("tab")

    # Type a domain in the address bar and press Ctrl/Cmd + Enter
    nav.type_in_awesome_bar(domain)
    nav.perform_key_combo_chrome(Keys.CONTROL, Keys.ENTER)

    # Verify navigation to the expected URL
    nav.url_contains(expected_url)
