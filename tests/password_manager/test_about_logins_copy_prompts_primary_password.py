import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import AboutLogins, AboutPrefs
from modules.util import BrowserActions

TEST_PAGE_URL = "https://mozilla.github.io/"
USERNAME = "username1"
PASSWORD = "password1"
PRIMARY_PASSWORD = "securePassword1"
ALERT_MESSAGE = "Primary Password successfully changed."


@pytest.fixture()
def test_case():
    return "2264690"


def test_about_logins_copy_prompts_primary_password(driver: Firefox):
    """
    C2264690 - Verify that clicking the 'Copy' password button prompts for the Primary Password before copying the password
    """

    # Instantiate objects
    about_logins = AboutLogins(driver)
    about_prefs = AboutPrefs(driver, category="privacy")
    ba = BrowserActions(driver)
    nav = Navigation(driver)

    # Have a Primary Password set
    about_prefs.create_primary_password(PRIMARY_PASSWORD, ALERT_MESSAGE, ba)

    # Have at least one saved login
    about_logins.open()
    about_logins.add_login(TEST_PAGE_URL, USERNAME, PASSWORD)

    # Click on the password "Copy" button
    about_logins.click_copy_password_button()

    # Enter the correct Primary Password
    about_logins.enter_primary_password(PRIMARY_PASSWORD)

    # Note: A checkmark and the text "Copied!" should appear as confirmation
    about_logins.element_visible("copied-button")

    # Verify that the password was correctly copied
    nav.clear_awesome_bar()
    nav.paste_in_awesome_bar()
    nav.verify_plain_text_in_input_awesome_bar(PASSWORD)
