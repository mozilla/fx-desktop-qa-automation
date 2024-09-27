import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, TabBar
from modules.page_object import AboutLogins, LoginAutofill


@pytest.fixture()
def test_case():
    return "2248176"


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return [("signon.rememberSignons", True)]


def test_auto_saved_generated_password_context_menu(driver: Firefox):
    """
    C2241087 - Securely Generated Password is auto-saved when generated from password field context menu
    """

    context_menu = ContextMenu(driver)
    tabs = TabBar(driver)
    login_autofill = LoginAutofill(driver).open()
    nav = Navigation(driver)
    about_logins = AboutLogins(driver)

    # Select "Suggest Strong Password..." from password field context menu
    password_field = login_autofill.get_element("password-login-field")
    login_autofill.context_click(password_field)
    context_menu.click_context_item("context-menu-suggest-strong-password")

    # Select "Use a Securely Generated Password" in password field and check the "Update password" doorhanger
    # is displayed
    with driver.context(driver.CONTEXT_CHROME):
        login_autofill.get_element("generated-securely-password").click()
        nav.element_visible("password-notification-key")
        nav.click_on("password-notification-key")
        update_doorhanger = nav.get_element("password-update-doorhanger")
        assert update_doorhanger.text == "Update password for mozilla.github.io?"

    # Navigate to about:logins page
    tabs.switch_to_new_tab()
    about_logins.open()

    # Verify the website address saves the correct value
    website_address_element = about_logins.get_element("website-address")
    assert website_address_element.get_attribute("href") == "https://mozilla.github.io/"

    # Verify the username field has no value
    username_element = about_logins.get_element("username-field")
    assert username_element.get_attribute("placeholder") == "(no username)"

    # Verify the password field is filled with a value
    password_element = about_logins.get_element("password-field")
    assert password_element.get_attribute("tabindex") == "-1"
