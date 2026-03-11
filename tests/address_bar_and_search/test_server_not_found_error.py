import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_error_page import ErrorPage


@pytest.fixture()
def test_case():
    return "3029186"


CHECK_SITE = "http://example"
SHORT_SITE = CHECK_SITE.split("/")[-1]
REDIRECT_URL = "www.example.com"
ERROR_TITLE = ["Server Not Found"]


def test_server_not_found_error(driver: Firefox):
    """
    C3029186 - This tests that when a user navigates to a non-existent site, a "Server Not Found" error is
    displayed. The error page contains the correct elements, and the suggested link redirects to the appropriate page.
    """

    # Instantiate objects
    nav = Navigation(driver)
    tabs = TabBar(driver)
    error_page = ErrorPage(driver)

    # Navigate to the desired site
    nav.search(CHECK_SITE)

    # Wait until the tab title updates to "Server Not Found"
    tabs.wait_for_tab_title("Problem loading page")

    # Verify title and short description on the error page
    error_page.verify_error_header(ERROR_TITLE, SHORT_SITE)

    # Verify the "Learn more" link redirects correctly
    error_page.click_learn_more_and_verify_redirect(REDIRECT_URL)
