import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar
from modules.page_object import AboutLogins, AboutPrefs, LoginAutofill
from modules.util import BrowserActions

CREDENTIAL_ORIGIN = "https://facebook.com"
USERNAME = "username"
PASSWORD = "password"
PRIMARY_PASSWORD = "securePassword1"
ALERT_MESSAGE = "Primary Password successfully changed."


@pytest.fixture()
def test_case():
    return "2245189"


def test_no_generated_password_options_with_pp_and_no_credentials(driver: Firefox):
    """
    C2245189 - Verify that Generated Password options are not available when no credentials are saved and a PP is set
    """

    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    ba = BrowserActions(driver)
    tabs = TabBar(driver)
    about_logins = AboutLogins(driver)
    login_autofill = LoginAutofill(driver)
    context_menu = ContextMenu(driver)

    # Have a Primary Password set
    about_prefs.create_primary_password(PRIMARY_PASSWORD, ALERT_MESSAGE, ba)

    # Open about:logins page and create a login entry
    tabs.switch_to_new_tab()
    about_logins.open()
    about_logins.add_login(CREDENTIAL_ORIGIN, USERNAME, PASSWORD)

    # Attempt to view the saved password in order to trigger the primary password prompt
    about_logins.element_visible("show-password-checkbox")
    about_logins.click_on("show-password-checkbox")

    # Dismiss the primary password prompt without entering the password
    about_logins.dismiss_primary_password_prompt()

    # Go to the test website
    tabs.switch_to_new_tab()
    login_autofill.open()

    # Right-click on the username field
    login_autofill.context_click("username-field")

    # Saved Password option is grayed out in the context menu
    context_menu.verify_item_disabled("context-menu-use-saved-password")

    # Right-click on the password field
    login_autofill.context_click("password-login-field")

    # Saved Password option is grayed out in the context menu
    context_menu.verify_item_disabled("context-menu-use-saved-password")

    # Suggest strong password option is grayed out in the context menu
    context_menu.verify_item_disabled("context-menu-suggest-strong-password")
