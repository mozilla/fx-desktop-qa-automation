import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.page_object_about_pages import AboutLogins
from modules.page_object_autofill import LoginAutofill

USERNAME = "testUser"
PASSWORD = "testPassword"
PASSWORD_EDIT = "12"
PASSWORD_EDITED = "testPassword12"


@pytest.fixture()
def test_case():
    return "2243020"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("signon.rememberSignons", True), ("signon.autofillForms", True)]


def test_private_browsing_dismiss_doorhanger_credentials(driver: Firefox):
    """
    C2243020 - [Private Mode] Verify that dismissed doorhanger is displayed for credentials in private mode
    """

    # Instantiate objects
    login_autofill = LoginAutofill(driver)
    nav = Navigation(driver)
    panel = PanelUi(driver)
    about_logins = AboutLogins(driver)

    # Open a private window and switch to it
    panel.open_and_switch_to_new_window("private")

    # Access a website that requires a username and password
    login_autofill.open()
    login_form = LoginAutofill.LoginForm(login_autofill)

    # Fill in any credentials and click on Log In
    login_form.fill_username(USERNAME)
    login_form.fill_password(PASSWORD)
    login_form.submit()

    # Check that there is no doorhanger displayed like in normal browsing mode
    nav.element_not_visible("password-notification-popup")

    # Check that there is a grey key icon displayed on the left part of the address bar
    nav.element_visible("password-notification-key")

    # Click on the grey icon
    nav.click_on("password-notification-key")

    # The "Save" doorhanger is displayed upon clicking the grey icon
    nav.element_visible("password-notification-popup")
    nav.wait_for_notification_popup_open()

    # Choose to save the credentials
    nav.element_clickable("password-notification-save-button")
    nav.click_on("password-notification-save-button")

    # Re-load the form
    login_autofill.open()

    # Select the previously saved credentials from the autocomplete dropdown
    login_form.select_saved_credentials(
        "username-login-field", "mozilla-github-credentials"
    )

    # Edit the password and click on "Log in"
    login_form = LoginAutofill.LoginForm(login_autofill)
    login_form.fill_password(PASSWORD_EDIT)
    login_form.submit()

    # The "Update" doorhanger is displayed
    nav.element_visible("password-notification-popup")

    # Confirm the changes in the doorhanger
    nav.click_on("password-notification-save-button")

    # The credentials have the password updated correctly, check this in about:logins
    about_logins.open()
    about_logins.click_copy_password_button()

    # Paste the copied password in the URL bar and verify the results
    nav.clear_awesome_bar()
    nav.paste_in_awesome_bar()

    # The password is correctly pasted
    nav.verify_plain_text_in_input_awesome_bar(PASSWORD_EDITED)
