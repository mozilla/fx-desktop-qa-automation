import pytest
from selenium.webdriver import Firefox


@pytest.fixture()
def test_case():
    return "3028712"


def test_searchbar_display_alpenglow_theme(driver: Firefox):
    """
    C3028997 - Search bar is correctly displayed on Alpenglow theme
    """
