import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ReaderView
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "130908"


READER_VIEW_URL: str = (
    "https://support.mozilla.org/en-US/kb/firefox-reader-view-clutter-free-web-pages"
)


def test_reader_view_open_close_using_searchbar(driver: Firefox) -> None:
    """
    C130908.1: Verify that Reader View can be opened and closed using the
    location bar (search bar) control.
    """
    page = GenericPage(driver, url=READER_VIEW_URL)
    rv = ReaderView(driver)

    # Open the Reader View through the search bar icon
    page.open()
    rv.open_reader_view_searchbar()
    if hasattr(rv, "wait_for_reader_view_open"):
        rv.wait_for_reader_view_open()

    # Close Reader View through the same toolbar control
    rv.close_reader_view_searchbar()
    if hasattr(rv, "wait_for_reader_view_closed"):
        rv.wait_for_reader_view_closed()


def test_reader_view_open_close_using_keys(driver: Firefox):
    """
    C130908.2: Verify that Reader View can be opened and closed using keyboard shortcuts.
    """
    page = GenericPage(driver, url=READER_VIEW_URL)
    rv = ReaderView(driver)

    page.open()

    # Open using the platform-specific shortcut (handled internally in ReaderView)
    rv.open_reader_view_keys()
    if hasattr(rv, "wait_for_reader_view_open"):
        rv.wait_for_reader_view_open()

    # Close using the same shortcut
    rv.close_reader_view_keys()
    if hasattr(rv, "wait_for_reader_view_closed"):
        rv.wait_for_reader_view_closed()
