import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup, ContextMenu, Navigation, TabBar
from modules.page_object import AboutLogins, LoginAutofill

UPDATE_DOORHANGER_TEXT = "Update password for mozilla.github.io?"
TEST_WEBSITE = "https://mozilla.github.io/"


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
    login_autofill.context_click("password-login-field")
    context_menu.click_and_hide_menu("context-menu-suggest-strong-password")

    # Select "Use a Securely Generated Password" in password field and check the "Update password" doorhanger
    with driver.context(driver.CONTEXT_CHROME):
        login_autofill.get_element("generated-securely-password").click()

    # Wait for password field to actually get filled
    login_autofill.expect(
        lambda _: login_autofill.get_element("password-login-field").get_attribute(
            "value"
        )
        != ""
    )

    # Verify the update doorhanger is displayed
    nav.expect(
        lambda _: nav.element_visible("password-notification-key")
    )
    nav.click_on("password-notification-key")
    autofill_popup_panel.expect(
        lambda _: UPDATE_DOORHANGER_TEXT
        in autofill_popup_panel.get_element("password-update-doorhanger").text
    )

    # Navigate to about:logins page
    tabs.switch_to_new_tab()
    about_logins.open()

    # Verify the website address saves the correct value
    about_logins.expect_element_attribute_contains(
        "website-address", "href", TEST_WEBSITE
    )

    # Verify the username field has no value
    about_logins.expect_element_attribute_contains(
        "about-logins-page-username-field", "placeholder", "(no username)"
    )

    # Verify the password field is filled with a value
    about_logins.expect_element_attribute_contains(
        "about-logins-page-password-hidden", "tabindex", "-1"
    )
