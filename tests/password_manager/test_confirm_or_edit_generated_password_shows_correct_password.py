from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import LoginAutofill


@pytest.fixture()
def test_case():
    return "2248183"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("signon.rememberSignons", True)]


def test_confirm_or_edit_generated_password_shows_correct_password(driver: Firefox):
    """
    C2248183 - Verify that the “Confirm/Retype Password” field autocomplete dropdown displays the previously edited and auto-saved generated password
    """

    # Instantiate objects
    login_autofill = LoginAutofill(driver)
    autofill_popup_panel = AutofillPopup(driver)

    # Access a website with a signup page
    login_autofill.open()
    # login_form = LoginAutofill.LoginForm(login_autofill)

    # Click on the password signup field and choose to "Use a Securely Generated" password
    login_autofill.click_on("password-signup-field")
    autofill_popup_panel.click_securely_generated_password()

    # Edit the generated password (e.g. add/remove characters) and click out-side of the field
