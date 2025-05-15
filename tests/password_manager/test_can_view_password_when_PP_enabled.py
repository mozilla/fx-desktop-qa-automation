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
    about_logins.click_add_login_button()

    # Complete all the fields with valid data and click the "Save" button.
    about_logins.create_new_login(
        {
            "origin": URL_TO_TEST,
            "username": USERNAME,
            "password": PASSWORD,
        }
    )

    # Select the "Use a primary password" check box to trigger the "Change Primary Password" window
    about_prefs.open()
    about_prefs.click_on("use-primary-password")
    primary_pw_popup = about_prefs.get_element("browser-popup")
    ba.switch_to_iframe_context(primary_pw_popup)

    # Current password field is empty and cannot be changed
    about_prefs.expect_element_attribute_contains(
        "current-password", "disabled", "true"
    )

    # Primary password can be changed
    about_prefs.get_element("enter-new-password").send_keys(PRIMARY_PASSWORD)
    about_prefs.get_element("reenter-new-password").send_keys(PRIMARY_PASSWORD)
    about_prefs.click_on("submit-password")

    # Check that the pop-up appears
    with driver.context(driver.CONTEXT_CHROME):
        alert = about_prefs.get_alert()
        alert.accept()

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
    about_logins.expect_element_attribute_contains(
        "about-logins-page-password-revealed", "type", "text"
    )
