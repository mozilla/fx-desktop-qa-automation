from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.page_object_about_pages import AboutLogins
from modules.page_object_autofill import LoginAutofill
from modules.page_object_prefs import AboutPrefs
from modules.util import BrowserActions

TEST_PAGE_URL = "https://mozilla.github.io/"
USERNAME = "username1"
PASSWORD = "password1"
PRIMARY_PASSWORD = "securePassword1"
ALERT_MESSAGE = "Primary Password successfully changed."
SECOND_ALERT_MESSAGE = "Please enter your Primary Password."


@pytest.fixture()
def test_case():
    return "2264689"


def test_about_logins_edit_prompts_primary_password(driver: Firefox):
    """
    C2264689 - Verify that clicking the 'Edit' button prompts for the Primary Password before entering edit mode
    """

    # Instantiate objects
    about_logins = AboutLogins(driver)
    login = LoginAutofill(driver)
    about_prefs = AboutPrefs(driver, category="privacy")
    ba = BrowserActions(driver)

    # Have a Primary Password set
    about_prefs.open()
    about_prefs.open_primary_password_popup(ba)
    about_prefs.set_primary_password(PRIMARY_PASSWORD)
    about_prefs.accept_alert_and_verify_text(ALERT_MESSAGE)

    # Have at least one saved login
    about_logins.open()
    about_logins.add_login(TEST_PAGE_URL, USERNAME, PASSWORD)

    # Click on the "Edit" button
    about_logins.click_on("edit-login")

    alert = about_prefs.get_alert()
    #alert.send_keys(PRIMARY_PASSWORD)
    #sleep(5)
    assert alert.text == SECOND_ALERT_MESSAGE
    alert.accept()
