import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.browser_object_tabbar import TabBar
from modules.page_object_error_page import ErrorPage


@pytest.fixture()
def test_case():
    return "3029188"


CHECK_SITE = "http://example"
SHORT_SITE = CHECK_SITE.split("/")[-1]
REDIRECT_URL = "https://www.example.com/"
ERROR_TITLES = ["Server Not Found"]


def test_server_not_found_error_on_private_window(driver: Firefox):
    """
    C3029188 - This tests that when a user navigates to a non-existent site in private window, a "Server Not Found"
    error is displayed. The error page contains the correct elements, and the suggested link redirects to the
    appropriate page.
    """

    # Instantiate objects
    nav = Navigation(driver)
    tabs = TabBar(driver)
    error_page = ErrorPage(driver)
    panel = PanelUi(driver)

    # Open a new private window and navigate to the desired site
    panel.open_and_switch_to_new_window("private")
    nav.search(CHECK_SITE)

    # Wait until the tab title updates to "Problem loading page"
    tabs.wait_for_tab_title("Problem loading page")

    # Verify title and short description on the error page
    error_page.verify_error_header(ERROR_TITLES, SHORT_SITE)

    # Verify the "Learn more" link redirects correctly
    error_page.click_learn_more_and_verify_redirect(REDIRECT_URL)
