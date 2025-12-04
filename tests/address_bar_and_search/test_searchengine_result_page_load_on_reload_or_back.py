import pytest
from selenium.webdriver import Firefox


@pytest.fixture()
def test_case():
    return "3028909"


def test_searchengine_result_page_load_on_reload_or_back(driver: Firefox):
    """
    C3028909 - Search Engine Result Page loads as a result of a reload or a back-button press
    """