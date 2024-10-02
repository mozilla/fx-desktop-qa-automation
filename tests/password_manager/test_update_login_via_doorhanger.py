import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TabBar
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import LoginAutofill


@pytest.fixture()
def test_case():
    return "2243013"


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return [("signon.rememberSignons", True), ("signon.autofillForms", True)]


def test_update_login_via_doorhanger(driver: Firefox):
    """
     C2243013 - Verify that Firefox successfully updates login credentials via the update password doorhanger and
    autofill them on subsequent access
    """

    login_autofill = LoginAutofill(driver).open()
    autofill_popup_panel = AutofillPopup(driver)
    tabs = TabBar(driver)
    nav = Navigation(driver)

    # Creating an instance of the LoginForm within the LoginAutofill page object
    login_form = LoginAutofill.LoginForm(login_autofill)

    # Fill in the login form in demo page and save the login credentials via the doorhanger
    login_form.fill_username("testUser")
    login_form.fill_password("testPassword")
    login_form.submit()
    autofill_popup_panel.click_doorhanger_button("save")

    tabs.switch_to_new_tab()

    # # Create new objects to prevent stale web elements
    new_login_autofill = LoginAutofill(driver).open()
    new_login_form = new_login_autofill.LoginForm(new_login_autofill)

    # Verify the initial length ot the password
    password_element = login_autofill.get_element("password-login-field")
    masked_password_value = password_element.get_attribute("value")
    assert len(masked_password_value) == 12

    # Add several characters inside the password field in demo page, update the login credentials via the doorhanger
    # and see the doorhanger is dismissed
    new_login_form.fill_password("Update")
    new_login_form.submit()

    autofill_popup_panel.click_doorhanger_button("update")
    nav.element_not_visible("password-notification-key")

    # Open the login form in a new tab and verify the password matches the length of the updated password
    tabs.switch_to_new_tab()
    login_autofill.open()

    password_element = login_autofill.get_element("password-login-field")
    masked_password_value = password_element.get_attribute("value")
    assert len(masked_password_value) == 18
