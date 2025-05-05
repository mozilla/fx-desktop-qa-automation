import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup, ContextMenu, Navigation, TabBar
from modules.page_object import AboutLogins, LoginAutofill


@pytest.fixture()
def test_case():
    return "2248176"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("signon.rememberSignons", True)]


def test_auto_saved_generated_password_context_menu(driver: Firefox):
    """
    C2248176 - Securely Generated Password is auto-saved when generated from password field context menu
    """
    # Instantiate objects
    context_menu = ContextMenu(driver)
    tabs = TabBar(driver)
    login_autofill = LoginAutofill(driver)
    nav = Navigation(driver)
    about_logins = AboutLogins(driver)
    autofill_popup_panel = AutofillPopup(driver)

    # Open login autofill test page and select "Suggest Strong Password..." from password field context menu
    login_autofill.open()
    password_field = login_autofill.get_element("password-login-field")
    login_autofill.context_click(password_field)
    context_menu.click_and_hide_menu("context-menu-suggest-strong-password")

    # Select "Use a Securely Generated Password" in password field and check the "Update password" doorhanger
    # is displayed
    with driver.context(driver.CONTEXT_CHROME):
        login_autofill.get_element("generated-securely-password").click()
        nav.element_visible("password-notification-key")
        nav.click_on("password-notification-key")
        update_doorhanger = autofill_popup_panel.get_element(
            "password-update-doorhanger"
        )
        assert update_doorhanger.text == "Update password for mozilla.github.io?"

    # Navigate to about:logins page
    tabs.switch_to_new_tab()
    about_logins.open()

    # Verify the website address saves the correct value
    about_logins.element_attribute_contains(
        "website-address", "href", "https://mozilla.github.io/"
    )

    # Verify the username field has no value
    about_logins.element_attribute_contains(
        "about-logins-page-username-field", "placeholder", "(no username)"
    )

    # Verify the password field is filled with a value
    about_logins.element_attribute_contains(
        "about-logins-page-password-hidden", "tabindex", "-1"
    )
