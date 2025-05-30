import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar
from modules.page_object import LoginAutofill

ABOUT_LOGINS_PAGE_TITLE = "Passwords"


@pytest.fixture()
def test_case():
    return "2241087"


@pytest.mark.ci
def test_about_logins_navigation_from_login_form_context_menu(driver: Firefox):
    """
    C2241087 - Verify that right-clicking the Username field in a login form and then the Manage Passwords option
    from context menu opens about:logins page in a new tab
    """
    # Instantiate objects
    context_menu = ContextMenu(driver)
    tabs = TabBar(driver)
    login = LoginAutofill(driver)

    # Access the manage passwords in context menu from the username field in the demo login form
    login.open()
    login.context_click("username-field")
    context_menu.click_and_hide_menu("context-menu-manage-passwords")

    # Verify that the about:logins page is opened in a new tab
    tabs.wait_for_num_tabs(2)
    tabs.title_contains(ABOUT_LOGINS_PAGE_TITLE)
