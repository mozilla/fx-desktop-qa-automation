import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import ContextMenu, TabBar
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "2241087"


URL_TEST_PAGE = "https://bsky.app/"


def test_about_logins_navigation_from_login_form_context_menu(driver: Firefox):
    """
    C2241087 - Verify that clicking the Username field and then the Manage Passwords option opens about:logins page in
    a new tab
    """

    context_menu = ContextMenu(driver)
    tabs = TabBar(driver)
    test_page = GenericPage(driver, url=URL_TEST_PAGE).open()

    test_page.find_element(By.CSS_SELECTOR, 'button[aria-label="Sign in"]').click()
    username_field = test_page.find_element(
        By.CSS_SELECTOR, 'input[aria-label="Username or email address"]'
    )
    test_page.context_click(username_field)
    context_menu.click_context_item("context-manage-passwords")
    tabs.wait_for_num_tabs(2)
    tabs.title_contains("Passwords")
