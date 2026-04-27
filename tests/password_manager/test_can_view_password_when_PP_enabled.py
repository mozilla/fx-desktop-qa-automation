import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.page_object import AboutLogins
from modules.page_object_prefs import AboutPrefs
from modules.util import BrowserActions

URL_TO_TEST = "https://mozilla.github.io/"
USERNAME = "username"
PASSWORD = "password"
PRIMARY_PASSWORD = "securePassword1"
ALERT_MESSAGE = "Primary Password successfully changed."


@pytest.fixture()
def test_case():
    return "2264688"


def test_password_can_be_shown(driver: Firefox):
    """
    C2264688: Verify that the Show Password button prompts for the Primary Password before revealing the saved login
    """
    # Instantiate object
    about_logins = AboutLogins(driver)
    about_prefs = AboutPrefs(driver, category="privacy")
    ba = BrowserActions(driver)

    # Open about:login and click on the "Add password" button
    about_logins.open()

    # Complete all the fields with valid data and click the "Save" button.
    about_logins.add_login(URL_TO_TEST, USERNAME, PASSWORD)

    # Select the "Use a primary password" check box to trigger the "Change Primary Password" window
    about_prefs.open()
    about_prefs.open_primary_password_popup(ba)

    # Current password field is empty and cannot be changed
    about_prefs.element_attribute_contains("current-password", "disabled", "true")

    # Primary password can be changed
    about_prefs.set_primary_password(PRIMARY_PASSWORD)

    # Check that the pop-up appears
    about_prefs.accept_alert_and_verify_text(ALERT_MESSAGE)

    about_logins.open()
    about_logins.click_on("show-password-checkbox")

    with driver.context(driver.CONTEXT_CHROME):
        driver.switch_to.window(driver.window_handles[-1])
        # Fetch a fresh reference to avoid staling
        primary_password_prompt = about_logins.get_element("primary-password-prompt")
        assert primary_password_prompt.is_displayed()

        primary_password_input_field = about_logins.get_element(
            "primary-password-dialog-input-field"
        )
        primary_password_input_field.send_keys(PRIMARY_PASSWORD)
        primary_password_input_field.send_keys(Keys.ENTER)

    # Verify that the password is unmasked by checking that the type is now text.
    driver.switch_to.window(driver.window_handles[0])
    about_logins.element_attribute_contains(
        "about-logins-page-password-revealed", "type", "text"
    )
