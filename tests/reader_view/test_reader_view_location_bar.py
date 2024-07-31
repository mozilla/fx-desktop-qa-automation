from selenium.webdriver import Firefox

from modules.browser_object import ReaderView
from modules.page_object import GenericPage

WIKI_URL = "https://en.wikipedia.org/wiki/United_States"


def test_reader_view_open_close_using_searchbar(driver: Firefox):
    """
    C130908.1: Ensure that reader view is opened and closed from the location bar
    """
    wiki_page = GenericPage(driver, url=WIKI_URL)
    reader_view = ReaderView(driver)

    wiki_page.open()
    reader_view.open_reader_view_searchbar()
    reader_view.close_reader_view_searchbar()


def test_reader_view_open_close_using_keys(driver: Firefox):
    """
    C130908.2: Ensure that the reader view is opened and closed using keys
    """
    wiki_page = GenericPage(driver, url=WIKI_URL)
    reader_view = ReaderView(driver)

    # DOES NOT WORK RIGHT NOW, NOT SURE WHY
    wiki_page.open()
    reader_view.open_reader_view_keys()
    reader_view.close_reader_view_keys()


# how do you press the view menu at the top in selenium?
