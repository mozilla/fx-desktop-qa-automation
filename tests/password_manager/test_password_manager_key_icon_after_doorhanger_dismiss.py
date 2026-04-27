import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.browser_object_navigation import Navigation
from modules.page_object_autofill import LoginAutofill

USERNAME = "testUser"
PASSWORD = "testPassword"


@pytest.fixture()
def test_case():
    return "2243019"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("signon.rememberSignons", True)]


def test_password_manager_key_icon_after_doorhanger_dismiss(driver: Firefox):
    """
    C2243019 - Verify that Password Manager key icon is displayed when the Password Manager's doorhanger is dismissed temporarily
    """

    # Instantiate objects
    login_autofill = LoginAutofill(driver)
    nav = Navigation(driver)
    autofill_popup_panel = AutofillPopup(driver)

    # Access a website that requires a username and password
    login_autofill.open()
    login_form = LoginAutofill.LoginForm(login_autofill)

    # Enter a username and password and click "Log in"
    login_form.fill_username(USERNAME)
    login_form.fill_password(PASSWORD)
    login_form.submit()

    # A doorhanger pops up and the Password Manager key icon is displayed on the left side of the location bar
    nav.element_visible("password-notification-key")
    nav.element_visible("password-notification-popup")

    # Dismiss the doorhanger
    autofill_popup_panel.dismiss_password_doorhanger()

    # The Password Manager key icon is displayed on the left side of the location bar
    nav.element_not_visible("password-notification-popup")

    # Click the Passowrd Manager key icon
    nav.click_on("password-notification-key")

    # The Password Manager dialog is displayed
    nav.element_visible("password-notification-popup")
