import os

import pytest
from selenium.webdriver import Firefox

from modules.page_object import GenericPdf


@pytest.fixture()
def test_case():
    return "1756769"


@pytest.fixture()
def delete_files_regex_string():
    return r".*i-9.pdf"


def test_download_pdf(
    driver: Firefox,
    fillable_pdf_url: str,
    downloads_folder: str,
    delete_files,
    wait_for_file_download,
):
    """
    C1756769: Verify that the user can Download a PDF

    Notes:
        - The native "Save File" picker is mocked on all platforms so the
          download runs headlessly in CI. Driving the OS file dialog is
          unreliable there (Linux Wayland cannot drive GTK pickers through
          desktop input, and Windows image-matching depends on the CI
          resolution/DPI/theme).
    """

    # Set the expected download path and the expected PDF name
    file_name = "i-9.pdf"
    saved_pdf_location = os.path.join(downloads_folder, file_name)

    # Initialize objects
    pdf_page = GenericPdf(driver, pdf_url=fillable_pdf_url)

    # Replace the native save dialog with a mock that returns our target path
    pdf_page.install_mock_file_picker(saved_pdf_location)
    try:
        pdf_page.click_download_button()
        pdf_page.wait_for_mock_file_picker()
    finally:
        pdf_page.cleanup_mock_file_picker()

    # Wait for the file to appear and finish downloading
    assert wait_for_file_download(saved_pdf_location), (
        f"File not found: {saved_pdf_location}"
    )
