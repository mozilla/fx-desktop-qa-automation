import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PrintPreview
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "1090684"


TEST_URL = "https://en.wikipedia.org"


def test_page_number_indicator_print_preview(driver: Firefox):
    """
    C1090684 - Verify page number indicator and navigation in Print Preview
    """
    # Instantiate objects
    print_preview = PrintPreview(driver)
    page = GenericPage(driver, url=TEST_URL)

    # Open test page
    page.open()

    # Open Print Preview
    print_preview.open_with_key_combo()
    print_preview.wait_for_preview_ready()

    # Verify indicator values
    current, total = print_preview.get_sheet_indicator_values()
    assert total >= 1, "Sheet count should be at least 1"
    assert 1 <= current <= total, "Current page should be within valid range"

    # Navigate to last page
    print_preview.go_to_last_page()
    assert print_preview.get_sheet_indicator_values() == (total, total)

    # Navigate to previous page
    print_preview.go_to_previous_page()
    assert print_preview.get_sheet_indicator_values() == (total - 1, total)

    # Navigate to first page
    print_preview.go_to_first_page()
    assert print_preview.get_sheet_indicator_values() == (1, total)

    # Navigate to next page
    print_preview.go_to_next_page()
    assert print_preview.get_sheet_indicator_values() == (2, total)
