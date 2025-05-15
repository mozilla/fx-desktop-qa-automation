import pytest
from selenium.webdriver import Firefox
from modules.browser_object import ContextMenu, Navigation
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import LoginAutofill


USERNAME = "testUser"
PASSWORD = "testPassword"
UPDATED_PASSWORD = "testPasswordUpdate"


@pytest.fixture()
def test_case():
    return "2243013"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("signon.rememberSignons", True), ("signon.autofillForms", True)]


def test_update_login_via_doorhanger(driver: Firefox):
    """
    C2243013 - Verify that Firefox successfully updates login credentials via the update password doorhanger and
    autofill them on subsequent access
    """
    # Instantiate objects
    login_autofill = LoginAutofill(driver)
    autofill_popup_panel = AutofillPopup(driver)
    nav = Navigation(driver)
    context_menu = ContextMenu(driver)

    # Creating an instance of the LoginForm within the LoginAutofill page object
    login_autofill.open()
    login_form = LoginAutofill.LoginForm(login_autofill)

    # Fill in the login form in demo page and save the login credentials via the doorhanger
    login_form.fill_username(USERNAME)
    login_form.fill_password(PASSWORD)
    login_form.submit()
    autofill_popup_panel.click_doorhanger_button("save")

    # Create new objects to prevent stale web elements
    new_login_autofill = LoginAutofill(driver).open()
    new_login_form = new_login_autofill.LoginForm(new_login_autofill)

    # Verify the initial password value
    password_element = login_autofill.get_element("password-login-field")
    login_autofill.wait.until(
        lambda _: password_element.get_attribute("value") == PASSWORD
    )

    # Add several characters inside the password field in demo page, update the login credentials via the doorhanger
    # and see the doorhanger is dismissed
    new_login_form.fill_password("Update")
    new_login_form.submit()

    autofill_popup_panel.click_doorhanger_button("update")
    nav.element_not_visible("password-notification-key")

    new_login_autofill.open()

    # Select Reveal password from password field context menu for headed run purpose only
    login_autofill.context_click("password-login-field")

    context_menu.click_and_hide_menu("context-menu-reveal-password")

    # Verify the password matches updated password value
    password_element = login_autofill.get_element("password-login-field")
    login_autofill.wait.until(
        lambda _: password_element.get_attribute("value") == UPDATED_PASSWORD
    )
