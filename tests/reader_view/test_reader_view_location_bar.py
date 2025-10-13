import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ReaderView
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "130908"


READER_VIEW_URL = (
    "https://support.mozilla.org/en-US/kb/firefox-reader-view-clutter-free-web-pages"
)


def test_reader_view_open_close_using_searchbar(driver: Firefox):
    """
    C130908.1: Verify that Reader View can be opened and closed using the
    location bar (search bar) control.
    """
    page = GenericPage(driver, url=READER_VIEW_URL)
    rv = ReaderView(driver)

    page.open()
    rv.open_reader_view_searchbar()
    rv.close_reader_view_searchbar()


def test_reader_view_open_close_using_keys(driver: Firefox):
    """
    C130908.2: Verify that Reader View can be opened and closed using keyboard shortcuts.
    """
    page = GenericPage(driver, url=READER_VIEW_URL)
    rv = ReaderView(driver)

    page.open()
    rv.open_reader_view_keys()
    rv.close_reader_view_keys()
