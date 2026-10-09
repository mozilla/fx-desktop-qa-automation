import os
from pathlib import Path
from shutil import copyfile

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PrintPreview
from modules.page_object_generics import GenericPdf


@pytest.fixture()
def test_case():
    return "38250"


@pytest.fixture()
def delete_files_regex_string():
    return r"i-9-printed\.pdf"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("print_printer", "Mozilla Save to PDF"),
        ("print.save_print_settings", False),
    ]


PDF_FILE_NAME = "i-9.pdf"
PRINTED_PDF_NAME = "i-9-printed.pdf"


def test_print_pdf_via_pdfjs(
    driver: Firefox,
    downloads_folder: str,
    delete_files,
    print_preview: PrintPreview,
    wait_for_file_download,
    tmp_path: Path,
):
    """
    C38250 - Verify that the user can print a PDF opened via pdf.js

    Notes:
        - The native "Save" picker is mocked on all platforms so the print-to-PDF
          save runs headlessly in CI. Driving the OS file dialog is unreliable
          there (Linux Wayland cannot drive GTK pickers through desktop input,
          and Windows image-matching depends on the CI resolution/DPI/theme).
    """
    saved_pdf_location = os.path.join(downloads_folder, PRINTED_PDF_NAME)

    # Copy sample pdf into temporary directory
    source = tmp_path / PDF_FILE_NAME
    copyfile(f"data/{PDF_FILE_NAME}", source)
    pdf_viewer = GenericPdf(driver, pdf_url=f"file://{source}")

    # Open print preview from pdf.js toolbar; destination defaults to Save to PDF
    pdf_viewer.click_print_button()
    print_preview.wait_for_page_to_load()
    print_preview.wait_for_preview_ready()

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
