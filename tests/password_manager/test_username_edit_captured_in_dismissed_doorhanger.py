import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.browser_object_navigation import Navigation
from modules.page_object_autofill import LoginAutofill

PASSWORD = "testPassword"
USERNAME = "testUsername"


@pytest.fixture()
def test_case():
    return "2244614"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("signon.rememberSignons", True)]


def test_username_edit_captured_in_dismissed_doorhanger(driver: Firefox):
    """
    C2244614 - Verify that username field edits are captured in the dismissed doorhanger
    """

    # Instantiate objects
    login_autofill = LoginAutofill(driver)
    nav = Navigation(driver)
    autofill_popup_panel = AutofillPopup(driver)

    # Access a website that requires a username and password
    login_autofill.open()
    login_form = LoginAutofill.LoginForm(login_autofill)

    # Fill in only the password field
    login_form.fill_password(PASSWORD)

    # Click the Password Manager key icon
    nav.click_on("password-notification-key")

    # Check that only password is displayed in the doorhanger
    autofill_popup_panel.verify_username_value(USERNAME)

    # Fill in the username field and click on the grey key icon from the address bar
    login_form.fill_password(PASSWORD)

    # Click the Password Manager key icon
    nav.click_on("password-notification-key")

    # The previously filled username is also added in the dismissed doorhanger

    # Edit the username field from the login form several times

    # Check if the edits are reflected in the dismissed doorhanger

    # Username field edits are captured in the dismissed doorhanger
