from pathlib import Path

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PrintPreview
from modules.page_object import GenericPdf


@pytest.fixture()
def test_case():
    return "1081124"


@pytest.fixture()
def delete_files_regex_string():
    return r"non-contiguous-print-range\.pdf"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("print_printer", "Mozilla Save to PDF"),
        ("print.save_print_settings", False),
    ]


FIXTURE = Path("data/pages/print_non_contiguous_ranges.html").resolve()
PDF_NAME = "non-contiguous-print-range.pdf"


def test_non_contiguous_page_ranges(
    driver: Firefox,
    downloads_folder: str,
    delete_files,
    print_preview: PrintPreview,
    wait_for_file_download,
):
    """C1081124 - Verify non-contiguous page ranges print successfully."""
    driver.get(FIXTURE.as_uri())
    print_preview.open_with_key_combo()
    print_preview.wait_for_preview_ready()

    # An out-of-range page should display an error and make the form invalid.
    print_preview.set_custom_page_range("4,10")
    print_preview.expect_invalid_custom_page_range()

    # The selected non-contiguous range should produce two preview sheets.
    print_preview.set_custom_page_range("4,9")
    print_preview.wait_for_sheet_count(expected=2)

    saved_pdf = Path(downloads_folder) / PDF_NAME
    print_preview.install_mock_file_picker(str(saved_pdf))
    try:
        print_preview.click_primary_button()
        print_preview.wait_for_mock_file_picker()
    finally:
        print_preview.cleanup_mock_file_picker()

    assert wait_for_file_download(str(saved_pdf)), f"File not found: {saved_pdf}"

    printed = GenericPdf(driver, pdf_url=saved_pdf.as_uri())
    assert printed.max_page == 2

    first_page_text = printed.get_page_text(1)
    second_page_text = printed.get_page_text(2)
    all_text = f"{first_page_text}\n{second_page_text}"

    assert "PRINT_PAGE_4" in first_page_text
    assert "PRINT_PAGE_9" in second_page_text
    for page_number in (1, 2, 3, 5, 6, 7, 8):
        assert f"PRINT_PAGE_{page_number}" not in all_text
