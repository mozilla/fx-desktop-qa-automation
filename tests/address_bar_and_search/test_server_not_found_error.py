import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_error_page import ErrorPage


@pytest.fixture()
def test_case():
    return "3029186"


CHECK_SITE = "http://example"
SHORT_SITE = CHECK_SITE.split("/")[-1]
ERROR_TITLES = ["Hmm. We’re having trouble finding that site."]


def test_server_not_found_error(driver: Firefox, version: str):
    """
    C1901393: - This tests that when a user navigates to a non-existent site, a "Server Not Found" error is
    displayed. The error page contains the correct elements, and the suggested link redirects to the appropriate page.
    """

    # Create objects
    nav = Navigation(driver)
    tabs = TabBar(driver)
    error_page = ErrorPage(driver)

    # Navigate to the desired site
    nav.search(CHECK_SITE)

    # Wait until the tab title updates to "Server Not Found"
    WebDriverWait(driver, 30).until(
        lambda d: tabs.get_tab_title(tabs.get_tab(1)) == "Server Not Found"
    )

    # Verify elements on the error page
    assert error_page.get_error_title() in ERROR_TITLES
    assert (
        f"We can’t connect to the server at {SHORT_SITE}"
        in error_page.get_error_short_description()
    )

    # Define all possible valid permission messages (exact matches) for different Firefox channels
    possible_permission_messages = [
        "Check that Firefox has permission to access the web (you might be connected but behind a firewall)",
        "Check that Firefox Developer Edition has permission to access the web (you might be connected but behind a "
        "firewall)",
        "Check that Nightly has permission to access the web (you might be connected but behind a firewall)",
    ]

    expected_texts = [
        "Try again later",
        "Check your network connection",
    ]

    items = error_page.get_error_long_description_items()
    assert len(items) >= 3

    # Verify that the first two bullet items exactly match the expected texts
    for i in range(2):
        assert items[i].text == expected_texts[i]

    # Verify that the third bullet item exactly matches one of the valid permission messages
    assert items[2].text in possible_permission_messages

    # Verify that the suggested link redirects to the correct page
    error_page.get_error_suggestion_link().click()
    nav.expect_in_content(EC.url_contains("https://www.example.com/"))
