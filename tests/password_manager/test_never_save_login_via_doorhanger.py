import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup, Navigation, TabBar
from modules.page_object import AboutPrefs, LoginAutofill
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "2243012"


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return [("signon.rememberSignons", True), ("signon.autofillForms", True)]


def test_never_save_login_via_doorhanger(driver: Firefox):
    """
    C22243012 - Verify that selecting the 'Never Save' option in the password doorhanger prevents Firefox from saving
    the login credentials. Ensure that on subsequent access, the username and password fields remain empty in the
    login form. Additionally, confirm that the demo page is correctly added to the 'Exceptions - Saved Passwords'
    list in the browser's preferences.
    """

    login_autofill = LoginAutofill(driver).open()
    autofill_popup_panel = AutofillPopup(driver)
    tabs = TabBar(driver)
    nav = Navigation(driver)
    ba = BrowserActions(driver)

    # Creating an instance of the LoginForm within the LoginAutofill page object
    login_form = LoginAutofill.LoginForm(login_autofill)

    # Fill in the login form in demo page, opt for Never Save the credentials via doorhanger and see the doorhanger is
    # dismissed
    login_form.fill_username("testUser")
    login_form.fill_password("testPassword")
    login_form.submit()

    autofill_popup_panel.click_doorhanger_button("never-save-login")
    nav.element_not_visible("password-notification-key")

    # Open demo page in a new tab
    tabs.switch_to_new_tab()
    login_autofill.open()

    # Verify the username and password filed have empty values
    username_element = login_autofill.get_element("username-login-field")
    assert username_element.get_attribute("value") == ""

    password_element = login_autofill.get_element("password-login-field")
    masked_password_value = password_element.get_attribute("value")
    assert len(masked_password_value) == 0

    # Navigate to about:preferences#privacy and open Exceptions - Saved Passwords modal
    about_prefs = AboutPrefs(driver, category="privacy").open()
    iframe = about_prefs.get_password_exceptions_popup_iframe()
    ba.switch_to_iframe_context(iframe)

    # Verify that the demo page used in the test appears in the Exceptions list
    password_exceptions_element = about_prefs.get_element("exceptions-item")
    assert (
        password_exceptions_element.get_attribute("origin")
        == "https://mozilla.github.io"
    )
