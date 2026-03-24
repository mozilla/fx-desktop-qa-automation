import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu
from modules.page_object import LoginAutofill


@pytest.fixture()
def test_case():
    return "2240903"


def test_use_saved_password_not_in_context_menu_without_saved_logins(driver: Firefox):
    """
    C2240903 - Verify that "Use Saved Password" option is not displayed in the context menu
    when right-clicking the username field of the Login form with no saved logins for the page
    """
    # Instantiate objects
    context_menu = ContextMenu(driver)
    login = LoginAutofill(driver)

    # Open the login autofill demo page and right-click the username field
    login.open()
    login.context_click("username-login-field")

    # Verify that "Use Saved Password" is not displayed in the context menu
    context_menu.element_not_visible("context-menu-use-saved-password")
