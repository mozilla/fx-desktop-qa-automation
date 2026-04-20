import pytest
from selenium.webdriver import Firefox

from modules.page_object_prefs import AboutPrefs
from modules.util import BrowserActions

PRIMARY_PASSWORD = "securePassword1"
ALERT_MESSAGE = "Primary Password successfully changed."
REMOVE_ALERT_MESSAGE = "You have deleted your Primary Password."


@pytest.fixture()
def test_case():
    return "2245182"


def test_delete_primary_password(driver: Firefox):
    """
    C2245182 - Verify that the Primary Password can be removed
    """

    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    ba = BrowserActions(driver)

    # Select the "Use a primary password" check box to trigger the "Change Primary Password" window
    about_prefs.open()
    about_prefs.open_primary_password_popup(ba)

    # Add primary passwords
    about_prefs.set_primary_password(PRIMARY_PASSWORD)

    # Check that the pop-up appears
    about_prefs.accept_alert_and_verify_text(ALERT_MESSAGE)

    # Uncheck the "Use a Primary Password" checkbox
    about_prefs.open()
    about_prefs.click_on("use-primary-password")

    # A "Remove Primary Password" prompt appears, containing a single input field for the current Primary Password
    primary_pw_popup = about_prefs.get_element("browser-popup")
    ba.switch_to_iframe_context(primary_pw_popup)

    # Input your current Primary Password and click Remove
    about_prefs.get_element("remove-current-password").send_keys(PRIMARY_PASSWORD)
    about_prefs.click_on("remove-password")

    # A "Password Change Succeeded" confirmation message appears, click "OK"
    about_prefs.accept_alert_and_verify_text(REMOVE_ALERT_MESSAGE)

    # "Use a Primary Password" checkbox is now unchecked given that the Primary Password has been removed
    about_prefs.open()
    checkbox = about_prefs.get_element("use-primary-password")
    assert not checkbox.is_selected()
