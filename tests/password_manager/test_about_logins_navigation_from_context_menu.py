import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar
from modules.page_object import LoginAutofill


@pytest.fixture()
def test_case():
    return "2241087"


def test_about_logins_navigation_from_login_form_context_menu(driver: Firefox):
    """
    C2241087 - Verify that right-clicking the Username field in a login form and then the Manage Passwords option
    from context menu opens about:logins page in a new tab
    """

    context_menu = ContextMenu(driver)
    tabs = TabBar(driver)
    login = LoginAutofill(driver).open()

    username_field = login.get_element("username-field")
    login.context_click(username_field)
    context_menu.click_context_item("context-manage-passwords")
    tabs.wait_for_num_tabs(2)
    tabs.title_contains("Passwords")
