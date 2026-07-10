import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ReaderView
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "130912"


def test_reader_view_close_from_sidebar(driver: Firefox, local_doc_path):
    """
    C130912: Ensure that reader view can be closed from the sidebar toolbar.
    """
    wiki_page = GenericPage(driver, url=local_doc_path)
    reader_view = ReaderView(driver)

    wiki_page.open()
    reader_view.open_reader_view_searchbar()
    reader_view.close_reader_view_by_x_button()
