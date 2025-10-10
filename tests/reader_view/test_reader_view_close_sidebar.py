import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ReaderView
from modules.page_object import GenericPage


@pytest.fixture()
def test_case() -> str:
    return "130912"


READER_VIEW_URL: str = (
    "https://support.mozilla.org/en-US/kb/firefox-reader-view-clutter-free-web-pages"
)


def test_reader_view_close_from_sidebar(driver: Firefox) -> None:
    """
    C130912: Ensure that Reader View can be closed from the sidebar toolbar.
    """
    page = GenericPage(driver, url=READER_VIEW_URL)
    rv = ReaderView(driver)

    # Open the article and bring up Reader View’s type/search toolbar
    page.open()
    rv.open_reader_view_searchbar()

    if hasattr(rv, "wait_for_reader_view_open"):
        rv.wait_for_reader_view_open()

    # Close Reader View from the sidebar toolbar
    rv.close_reader_view_searchbar()

    if hasattr(rv, "wait_for_reader_view_closed"):
        rv.wait_for_reader_view_closed()
    else:
        rv.element_not_visible("reader-view-controls")
