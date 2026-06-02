import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TabBar
from modules.page_object import AboutLogins, AboutProtections

TEST_PAGE_URL = "https://mozilla.github.io/"
USERNAME = "username1"
PASSWORD = "password1"
LOGIN_URL = "about:logins"


@pytest.fixture()
def test_case():
    return "448326"


def test_passwords_appear_in_firefox_lockwise(driver: Firefox):
    """
    C448326 - Passwords appear in Firefox Lockwise
    """

    # Instantiate objects
    protection = AboutProtections(driver)
    about_logins = AboutLogins(driver)
    tabs = TabBar(driver)
    nav = Navigation(driver)

    # Open about:logins and have at least one login is saved
    about_logins.open()
    about_logins.add_login(TEST_PAGE_URL, USERNAME, PASSWORD)

    # Reach "about:protections"
    protection.open()

    # "x password stored securely." text is correctly displayed
    protection.verify_lockwise_scanned_text(expected_count=1)

    # Click on the "Manage Passwords" button
    protection.click_on("manage-passwords-button")

    # about:logins in opened in a new tab
    tabs.wait_and_switch_to_new_tab()
    nav.url_contains(LOGIN_URL)
