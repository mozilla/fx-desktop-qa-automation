from selenium.webdriver import Firefox

from modules.browser_object import ReaderView
from modules.page_object import GenericPage

READER_VIEW_URL = (
    "https://support.mozilla.org/en-US/kb/firefox-reader-view-clutter-free-web-pages"
)


def test_reader_view_close_from_sidebar(driver: Firefox):
    """
    C130912: Ensures that the reader view can be closed from the sidebar toolbar.
    """
    wiki_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)

    wiki_page.open()
    reader_view.open_reader_view_searchbar()
    reader_view.close_reader_view_searchbar()
