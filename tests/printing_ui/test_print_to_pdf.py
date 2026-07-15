import os
import time

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PrintPreview


@pytest.fixture()
def test_case():
    return "965142"


@pytest.fixture()
def delete_files_regex_string():
    return r".*Example Domain.pdf"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("print_printer", "Mozilla Save to PDF"),
        ("print.save_print_settings", False),
    ]


TEST_PAGE = "https://example.com"
DEFAULT_NAME = "Example Domain.pdf"


def wait_for_file_download(file_path, timeout=10, interval=0.5) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(file_path):
            return True
        time.sleep(interval)
    return False


def test_print_to_pdf(
    driver: Firefox,
    downloads_folder: str,
    delete_files,
    print_preview: PrintPreview,
):
    """
    C965142 - Verify that the user can print a webpage to PDF

    Notes:
        - The native "Save" picker is mocked on all platforms so the print-to-PDF
          save runs headlessly in CI. Driving the OS file dialog is unreliable
          there (Linux Wayland cannot drive GTK pickers through desktop input,
          and Windows image-matching depends on the CI resolution/DPI/theme).
    """
    saved_pdf_location = os.path.join(downloads_folder, DEFAULT_NAME)

    driver.get(TEST_PAGE)

    # Open Print via the Hamburger Menu; destination defaults to Save to PDF
    print_preview.open_and_load_print_from_panelui()

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
