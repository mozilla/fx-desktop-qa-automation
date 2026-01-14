from selenium.webdriver import Firefox

from modules.browser_object import PrintPreview

TEST_PAGE = "https://en.wikipedia.org"


def test_page_number_indicator_print_preview(
    driver: Firefox, print_preview: PrintPreview
):
    """C965139 - Check for print preview modal (Key Combo)"""
    driver.get(TEST_PAGE)

    print_preview.open_with_key_combo()
    print_preview.wait_for_preview_ready()

    # indicator displayed
    assert "of" in print_preview.get_sheet_indicator_text()

    # navigation works
    print_preview.go_to_last_page()
    print_preview.go_to_previous_page()
    print_preview.go_to_first_page()
    print_preview.go_to_next_page()
