import logging

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_error_page import ErrorPage


@pytest.fixture()
def test_case():
    return "1901393"


CHECK_SITE = "http://cnn"
SHORT_SITE = CHECK_SITE.split("/")[-1]

ERROR_TITLES = ["Hmm. We’re having trouble finding that site."]


@pytest.mark.xfail
def test_server_not_found_error(driver: Firefox):
    """
    C1901393: - This tests that when a user navigates to a non-existent site, a "Server Not Found" error is
    displayed. The error page contains the correct elements, and the suggested link redirects to the appropriate page.
    """

    # Create objects
    logging.info("error titles")
    logging.info(ERROR_TITLES)
    nav = Navigation(driver)
    tabs = TabBar(driver)
    error_page = ErrorPage(driver)

    nav.search(CHECK_SITE)

    # Verify the tab title
    WebDriverWait(driver, 30).until(
        lambda d: tabs.get_tab_title(tabs.get_tab(1)) == "Server Not Found"
    )

    # Verify elements on the error page
    error_title = error_page.get_error_title()
    assert (
        error_title in ERROR_TITLES
    ), f"Expected error title text not found. Actual: {error_title}"

    error_short_description = error_page.get_error_short_description()
    assert (
        f"We can’t connect to the server at {SHORT_SITE}" in error_short_description
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
