import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.browser_object_tabbar import TabBar
from modules.page_object_error_page import ErrorPage


@pytest.fixture()
def test_case():
    return "3029186"


CHECK_SITE = "http://example"
SHORT_SITE = CHECK_SITE.split("/")[-1]
REDIRECT_URL = "https://www.example.com/"
ERROR_TITLES = ["Hmm. We’re having trouble finding that site."]
POSSIBLE_PERMISSION_MESSAGES = [
    "Check that Firefox has permission to access the web (you might be connected but behind a firewall)",
    "Check that Firefox Developer Edition has permission to access the web (you might be connected but behind a "
    "firewall)",
    "Check that Nightly has permission to access the web (you might be connected but behind a firewall)",
]
EXPECTED_TEXTS = ["Try again later", "Check your network connection"]


def test_server_not_found_error_on_private_window(driver: Firefox, version: str):
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

    panel.open_and_switch_to_new_window("private")
    nav.search(CHECK_SITE)

    # Wait until the tab title updates to "Server Not Found"
    tabs.wait_for_tab_title("Server Not Found")

    # Verify elements on the error page
    error_page.verify_error_header(ERROR_TITLES, SHORT_SITE)
    error_page.verify_error_bullets(EXPECTED_TEXTS, POSSIBLE_PERMISSION_MESSAGES)

    # Verify the suggestion link redirects correctly
    error_page.click_suggestion_and_verify_redirect(REDIRECT_URL)
