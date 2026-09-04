import pytest
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver import Firefox

from modules.browser_object import FindToolbar, Navigation
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "127261"


FIRST_PAGE = "https://www.mozilla.org/en-US/"
FIRST_PAGE_URL_PART = "mozilla.org"
SECOND_PAGE = "https://en.wikipedia.org/wiki/Firefox"
SECOND_PAGE_URL_PART = "wikipedia.org"
SEARCH_TERM = "firefox"


def test_find_toolbar_persists_after_back_forward(
    driver: Firefox,
    find_toolbar: FindToolbar,
):
    """
    C127261: Verify that navigation back and forward on a page works properly

    Arguments:
        find_toolbar: instantiation of FindToolbar BOM.
    """
    nav = Navigation(driver)

    # Visit two pages in the same tab, so there is history in both directions
    GenericPage(driver, url=FIRST_PAGE).open()
    GenericPage(driver, url=SECOND_PAGE).open()

    find_toolbar.open_with_key_combo()
    find_toolbar.find(SEARCH_TERM)

    def shows_search_term(_):
        """The findbar is torn down and rebuilt while the page loads"""
        try:
            find_bar = find_toolbar.get_element("find-toolbar-input")
            return (
                find_bar.is_displayed()
                and find_bar.get_property("value") == SEARCH_TERM
            )
        except (NoSuchElementException, StaleElementReferenceException):
            return False

    # Back to the previous page, the findbar stays open with the term in it
    nav.click_back_button()
    nav.url_contains(FIRST_PAGE_URL_PART)
    find_toolbar.expect(shows_search_term)

    # Forward to the next page
    nav.click_forward_button()
    nav.url_contains(SECOND_PAGE_URL_PART)
    find_toolbar.expect(shows_search_term)
