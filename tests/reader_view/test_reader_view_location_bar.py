import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ReaderView
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "130908"


def test_reader_view_open_close_using_searchbar(driver: Firefox, local_doc_path):
    """
    C130908.1: Ensure that reader view is opened and closed from the location bar
    """
    wiki_page = GenericPage(driver, url=local_doc_path)
    reader_view = ReaderView(driver)

    wiki_page.open()
    reader_view.open_reader_view_searchbar()
    reader_view.close_reader_view_searchbar()


def test_reader_view_open_close_using_keys(driver: Firefox, local_doc_path):
    """
    C130908.2: Ensure that the reader view is opened and closed using keys
    """
    wiki_page = GenericPage(driver, url=local_doc_path)
    reader_view = ReaderView(driver)

    wiki_page.open()
    reader_view.open_reader_view_keys()
    reader_view.close_reader_view_keys()
