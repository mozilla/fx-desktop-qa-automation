import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PrintPreview
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "2006919"


TEST_URL = "https://en.wikipedia.org"


def test_page_number_indicator_print_preview(driver: Firefox):
    """C2006919 - Verify page number indicator and navigation in Print Preview"""
    # Instantiate objects
    print_preview = PrintPreview(driver)
    page = GenericPage(driver, url=TEST_URL)

    page.open()

    # Open Print Preview
    print_preview.open_with_key_combo()
    print_preview.wait_for_preview_ready()
    print_preview.hover_preview()

    # Indicator displayed
    assert "of" in print_preview.get_sheet_indicator_text()

    # Navigation between pages
    print_preview.go_to_last_page()
    print_preview.go_to_previous_page()
    print_preview.go_to_first_page()
    print_preview.go_to_next_page()
