import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.browser_object_navigation import Navigation
from modules.page_object_about_pages import AboutLogins
from modules.page_object_autofill import LoginAutofill

PASSWORD = "testPassword"
USERNAME = "testUsername"


@pytest.fixture()
def test_case():
    return "2244613"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("signon.rememberSignons", True)]


def test_add_username_via_doorhanger(driver: Firefox):
    """
    C2244613 - Verify that a username can be added in doorhanger
    """

    # Instantiate objects
    login_autofill = LoginAutofill(driver)
    nav = Navigation(driver)
    autofill_popup_panel = AutofillPopup(driver)
    about_logins = AboutLogins(driver)

    # Access a website that requires a username and password
    login_autofill.open()
    login_form = LoginAutofill.LoginForm(login_autofill)

    # Fill in only the password field
    login_form.fill_password(PASSWORD)

    # Click the Password Manager key icon
    nav.click_on("password-notification-key")

    # The Password Manager dialog is displayed
    nav.element_visible("password-notification-popup")

    # Fill in the username field with a username and Save the changes
    autofill_popup_panel.type_username_in_password_doorhanger(USERNAME)
    autofill_popup_panel.click_doorhanger_button("save")

    # Password saved message is displayed -> check about:logins
    nav.element_visible("confirmation-hint")
    about_logins.open()
    about_logins.assert_username_present(USERNAME)
