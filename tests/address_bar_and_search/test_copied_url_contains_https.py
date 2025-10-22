import pytest
from selenium.webdriver import Firefox, Keys

from modules.browser_object import Navigation

TEST_WEBSITE = "https://www.firefox.com/"
TEXT = "https"


@pytest.fixture()
def test_case():
    return "3028769"


def test_copied_url_contains_https(driver: Firefox):
    """
    C3028712 - URLs copied from address bar contain https tags
    """

    # Instantiate objects
    nav = Navigation(driver)

    # Input a URL in the address bar and hit enter
    nav.type_in_awesome_bar(TEST_WEBSITE + Keys.ENTER)

    # Check that HTTPS is NOT displayed in the address bar for the website
    nav.verify_https_hidden_in_address_bar()

    # Click on the URL bar once and hit CTRL/CMD+C to copy the link
    nav.click_in_awesome_bar()
    nav.perform_key_combo(Keys.COMMAND, "c")

    # Open a new tab and paste (CTRL/CMD+V) the link
    nav.open_and_switch_to_new_window("tab")
    nav.click_in_awesome_bar()
    nav.perform_key_combo(Keys.COMMAND, "v")

    # Check that full link, including https://, is pasted in the address bar
    nav.verify_address_bar_value_prefix("https://")
