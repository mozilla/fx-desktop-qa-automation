import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, TabBar
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import LoginAutofill


@pytest.fixture()
def test_case():
    return "2243016"


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return [("signon.rememberSignons", True), ("signon.autofillForms", True)]


def test_save_login_via_doorhanger(driver: Firefox):
    """
    C2243016 -  Verify that Firefox successfully saves login credentials via the save password doorhanger and
    autofill them on subsequent access
    """

    login_autofill = LoginAutofill(driver).open()
    autofill_popup_panel = AutofillPopup(driver)
    tabs = TabBar(driver)
    nav = Navigation(driver)
    context_menu = ContextMenu(driver)

    # Creating an instance of the LoginForm within the LoginAutofill page object
    login_form = LoginAutofill.LoginForm(login_autofill)

    # Fill in the login form in demo page, save the login credentials via the doorhanger and see the doorhanger is
    # dismissed
    login_form.fill_username("testUser")
    login_form.fill_password("testPassword")
    login_form.submit()

    autofill_popup_panel.click_doorhanger_button("save")
    nav.element_not_visible("password-notification-key")

    # Open demo page in a new tab
    tabs.switch_to_new_tab()
    login_autofill.open()

    # Verify the username field has the saved value
    username_element = login_autofill.get_element("username-login-field")
    assert username_element.get_attribute("value") == "testUser"

    # Select Reveal password from password field context menu for headed run purpose only
    password_field = login_autofill.get_element("password-login-field")
    login_autofill.context_click(password_field)
    context_menu.click_context_item("context-menu-reveal-password")

    # Verify the password field is filled with a value that match the length of the saved password
    password_element = login_autofill.get_element("password-login-field")
    assert password_element.get_attribute("value") == "testPassword"
