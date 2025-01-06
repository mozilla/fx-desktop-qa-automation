import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PrintPreview


@pytest.fixture()
def test_case():
    return "965139"


TEST_PAGE = "https://en.wikipedia.org"


def test_print_preview_menu(driver: Firefox):
    """C965139 - Check for print preview modal (PanelUI)"""
    driver.get(TEST_PAGE)
    print_preview = PrintPreview(driver)
    print_preview.open()


@pytest.mark.ci
def test_print_preview_keys(driver: Firefox):
    """C965139 - Check for print preview modal (Key Combo)"""
    driver.get(TEST_PAGE)
    print_preview = PrintPreview(driver)
    print_preview.open_with_key_combo()
