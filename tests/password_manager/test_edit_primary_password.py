import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs
from modules.util import BrowserActions

PRIMARY_PASSWORD = "securePassword1"
ALERT_MESSAGE = "Primary Password successfully changed."
NEW_PRIMARY_PASSWORD = "securePasswordNew"


@pytest.fixture()
def test_case():
    return "2245180"


@pytest.fixture()
def hard_quit():
    return True


def test_edit_primary_password(driver: Firefox):
    """
    C2245180 - Verify that the Primary Password can be successfully changed
    """

    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    ba = BrowserActions(driver)

    # Select the "Use a primary password" check box to trigger the "Change Primary Password" window
    about_prefs.open()
    about_prefs.open_primary_password_popup(ba)

    # Primary password can be changed
    about_prefs.set_primary_password(PRIMARY_PASSWORD)

    # Check that the pop-up appears
    about_prefs.accept_alert_and_verify_text(ALERT_MESSAGE)

    # Click on the Change Primary Password button
    about_prefs.open()
    about_prefs.click_on("change-primary-password")

    # Input your current Primary Password followed by a new Primary Password(confirming it in the second field)
    primary_pw_popup = about_prefs.get_element("browser-popup")
    ba.switch_to_iframe_context(primary_pw_popup)
    about_prefs.get_element("current-primary-password").send_keys(PRIMARY_PASSWORD)
    about_prefs.get_element("enter-new-password").send_keys(NEW_PRIMARY_PASSWORD)
    about_prefs.get_element("reenter-new-password").send_keys(NEW_PRIMARY_PASSWORD)
    about_prefs.click_on("submit-password")

    # Check that the pop-up appears
    about_prefs.accept_alert_and_verify_text(ALERT_MESSAGE)
