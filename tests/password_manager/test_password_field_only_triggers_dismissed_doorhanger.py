import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_autofill import LoginAutofill

PASSWORD = "testPassword"


@pytest.fixture()
def test_case():
    return "2244612"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("signon.rememberSignons", True)]


def test_password_field_only_triggers_dismissed_doorhanger(driver: Firefox):
    """
    C2244612 - Verify that filling in only the password field triggers the dismissed doorhanger
    """

    # Instantiate objects
    login_autofill = LoginAutofill(driver)
    nav = Navigation(driver)

    # Access a website that requires a username and password
    login_autofill.open()
    login_form = LoginAutofill.LoginForm(login_autofill)

    # Fill in only the password field
    login_form.fill_password(PASSWORD)

    # The grey key icon is displayed on the left side of the address bar (dismissed doorhanger)
    nav.element_visible("password-notification-key")

    # Click the Password Manager key icon
    nav.click_on("password-notification-key")

    # The Password Manager dialog is displayed
    nav.element_visible("password-notification-popup")

    # Dismiss the doorhanger
    nav.dismiss_password_doorhanger()

    # The doorhanger is closed and the grey key icon is still displayed
    nav.element_not_visible("password-notification-popup")
    nav.element_visible("password-notification-key")

    # Click again on the grey key icon
    nav.click_on("password-notification-key")

    # The doorhanger is displayed again
    nav.element_visible("password-notification-popup")
