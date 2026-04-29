import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutLogins
from modules.page_object_prefs import AboutPrefs
from modules.util import BrowserActions

TEST_PAGE_URL = "https://mozilla.github.io/"
USERNAME = "username1"
PASSWORD = "password1"
PRIMARY_PASSWORD = "securePassword1"
ALERT_MESSAGE = "Primary Password successfully changed."
NEW_USERNAME = "new username"


@pytest.fixture()
def test_case():
    return "2264689"


def test_about_logins_edit_prompts_primary_password(driver: Firefox):
    """
    C2264689 - Verify that clicking the 'Edit' button prompts for the Primary Password before entering edit mode
    """

    # Instantiate objects
    about_logins = AboutLogins(driver)
    about_prefs = AboutPrefs(driver, category="privacy")
    ba = BrowserActions(driver)

    # Have a Primary Password set
    about_prefs.create_primary_password(PRIMARY_PASSWORD, ALERT_MESSAGE, ba)

    # Have at least one saved login
    about_logins.open()
    about_logins.add_login(TEST_PAGE_URL, USERNAME, PASSWORD)

    # Click on the "Edit" button
    about_logins.click_on("edit-login")

    # Enter the correct Primary Password
    about_logins.enter_primary_password(PRIMARY_PASSWORD)

    # The Edit mode is opened, change username and verify the field is changed
    about_logins.get_element("about-logins-page-username-field").send_keys(NEW_USERNAME)
    about_logins.click_on("save-edited-login")
    about_logins.element_attribute_contains(
        "about-logins-page-username-field", "value", NEW_USERNAME
    )
