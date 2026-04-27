import os
import time

import pytest
from selenium.webdriver import Firefox

from modules.page_object_generics import GenericPdf

PDF_FILE_NAME = "i-9.pdf"
DOWNLOADED_PDF_REGEX = r"i-9.*\.pdf"
DOWNLOAD_TIMEOUT_SEC = 5.0
POLL_INTERVAL_SEC = 1.0


def _wait_for_file_download(
    saved_pdf_path, timeout=DOWNLOAD_TIMEOUT_SEC, interval=POLL_INTERVAL_SEC
) -> None:
    """Wait until file exists on disk or raise a pytest failure."""

    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(saved_pdf_path):
            initial_size = os.path.getsize(saved_pdf_path)
            time.sleep(interval)
            final_size = os.path.getsize(saved_pdf_path)

            if initial_size == final_size and final_size > 0:
                return True

        time.sleep(interval)

    pytest.fail(f"The file was not downloaded within {timeout:.1f} seconds.")
    return None


@pytest.fixture()
def test_case():
    return "1020326"


@pytest.fixture()
def delete_files_regex_string():
    """Regex used by the cleanup fixture to remove downloaded files."""
    return DOWNLOADED_PDF_REGEX


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


@pytest.mark.headed
def test_download_pdf_with_form_fields(
    driver: Firefox,
    pdf_viewer: GenericPdf,
    sys_platform,
    delete_files,
    downloads_folder: str,
    delete_files_regex_string,
):
    """
    C1020326 Download pdf with form fields

    Arguments:
        sys_platform: Current System Platform Type
        pdf_viewer: Fixture returning instance of GenericPdf with correct path.
        downloads_folder: Fixture returning downloads folder path
        delete_files: Fixture to remove the files after the test finishes
    """
    # Fill in the name field and trigger download
    pdf_viewer.fill_element("first-name-field", "Mark")
    pdf_viewer.click_download_button()

    # Allow time for the download dialog to appear and handle the prompt
    time.sleep(2)

    # Handle OS download prompt
    pdf_viewer.handle_os_download_confirmation()

    # Set the expected download path and the expected PDF name
    saved_pdf_path = os.path.join(downloads_folder, PDF_FILE_NAME)

    # Verify if the file exists
    _wait_for_file_download(saved_pdf_path)

    # Open the saved pdf and check if the edited field is displayed
    driver.get("file://" + os.path.realpath(saved_pdf_path))
    pdf_viewer.element_visible("edited-name-field")
