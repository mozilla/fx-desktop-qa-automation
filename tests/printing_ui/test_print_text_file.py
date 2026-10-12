import os
from pathlib import Path

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PrintPreview
from modules.page_object import GenericPdf


@pytest.fixture()
def test_case():
    return "38242"


@pytest.fixture()
def delete_files_regex_string():
    return r"print_sample\.pdf"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("print_printer", "Mozilla Save to PDF"),
        ("print.save_print_settings", False),
    ]


FIXTURE = Path("data/pages/print_sample.txt").resolve()
SAVED_NAME = "print_sample.pdf"
START_MARKER = "THIS LINE IS VERY IMPORTANT!"
TAIL_MARKER = "The footer is everything from the end of this sentence"
PAGE_RANGE = "1-3"
RANGE_SHEETS = 3


def _pdf_text(driver: Firefox) -> str:
    """Read every page from pdf.js and collapse whitespace between text items."""
    with driver.context(driver.CONTEXT_CONTENT):
        text = driver.execute_async_script(
            """
            const done = arguments[0];
            (async () => {
                const app = window.PDFViewerApplication;
                await app.initializedPromise;
                const doc = app.pdfDocument;
                const parts = [];
                for (let i = 1; i <= doc.numPages; i++) {
                    const page = await doc.getPage(i);
                    const content = await page.getTextContent();
                    parts.push(content.items.map(item => item.str).join(" "));
                }
                done(parts.join("\\n"));
            })().catch(error => done({ error: String(error) }))
            """
        )
    assert isinstance(text, str), text
    return " ".join(text.split())


def test_print_text_file(
    driver: Firefox,
    downloads_folder: str,
    delete_files,
    print_preview: PrintPreview,
    wait_for_file_download,
):
    """
    C38242 - Verify that text files are successfully printed.

    Notes:
        - The native "Save" picker is mocked on all platforms so the print-to-PDF
          save runs headlessly in CI. Driving the OS file dialog is unreliable
          there (Linux Wayland cannot drive GTK pickers through desktop input,
          and Windows image-matching depends on the CI resolution/DPI/theme).
    """
    saved_pdf_location = os.path.join(downloads_folder, SAVED_NAME)

    # Open sample text file on browser and open print preview using keyboard shortcut
    driver.get(FIXTURE.as_uri())
    print_preview.open_with_key_combo()
    print_preview.wait_for_preview_ready()

    _, sheet_count = print_preview.get_sheet_indicator_values()
    assert sheet_count > RANGE_SHEETS, "Fixture must span more than the printed range"

    # Set custom range for pages to be printed
    print_preview.set_custom_page_range(PAGE_RANGE)
    print_preview.wait_for_sheet_count(RANGE_SHEETS)

    # Replace the native save dialog with a mock that returns our target path
    print_preview.install_mock_file_picker(saved_pdf_location)
    try:
        print_preview.click_primary_button()
        print_preview.wait_for_mock_file_picker()
    finally:
        print_preview.cleanup_mock_file_picker()

    assert wait_for_file_download(saved_pdf_location), (
        f"File not found: {saved_pdf_location}"
    )

    # Open downloaded PDF via pdf.js and ensure contents are as expected
    saved = GenericPdf(driver, pdf_url=Path(saved_pdf_location).as_uri())
    assert saved.max_page == RANGE_SHEETS
    text = _pdf_text(driver)
    assert START_MARKER in text
    assert TAIL_MARKER not in text
