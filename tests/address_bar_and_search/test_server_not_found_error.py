import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_error_page import ErrorPage


@pytest.fixture()
def add_prefs():
    return [
        ("browser.search.region", "US"),
    ]


def test_server_not_found_error(driver: Firefox):
    """
    C1901393: - This tests that when a user navigates to a non-existent site, a "Server Not Found" error is
    displayed. The error page contains the correct elements, and the suggested link redirects to the appropriate page.
    """

    # Create objects
    nav = Navigation(driver).open()
    tabs = TabBar(driver)
    error_page = ErrorPage(driver)

    nav.search("http://cnn")

    # Verify the tab title
    WebDriverWait(driver, 30).until(
        lambda d: tabs.get_tab_title(tabs.get_tab(1)) == "Server Not Found"
    )

    # Verify elements on the error page
    error_title = error_page.get_error_title()
    assert (
        error_title == "Hmm. We’re having trouble finding that site."
    ), f"Expected error title text not found. Actual: {error_title}"

    error_short_description = error_page.get_error_short_description()
    assert (
        error_short_description
        == "We can’t connect to the server at cnn. Did you mean to go to www.cnn.com?"
    ), (
        f"Expected error short description text not found."
        f"Actual: {error_short_description}"
    )

    error_long_description_items = error_page.get_error_long_description_items()
    expected_texts = [
        "Try again later",
        "Check your network connection",
        "Check that Firefox has permission to access the web (you might be connected but behind a firewall)",
    ]

    for i, item in enumerate(error_long_description_items):
        assert (
            item.text == expected_texts[i]
        ), f"Expected error long description item text not found. Actual: {item.text}"

    try_again_button = error_page.get_try_again_button()
    assert try_again_button.is_displayed(), "The 'Try Again' button is not displayed"

    # Verify that the suggested link redirects to the correct page
    error_page.get_error_suggestion_link().click()
    nav.expect_in_content(EC.url_contains("https://www.cnn.com/"))
