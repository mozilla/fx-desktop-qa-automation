import os
import time

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.page_object import GenericPdf

@pytest.fixture()
def test_case():
    return "1020327"

PDF_FILE_NAME = "i-9.pdf"
DOWNLOADED_PDF_REGEX = r"i-9.*\.pdf"
DOWNLOAD_TIMEOUT_SEC = 5.0
POLL_INTERVAL_SEC = 1.0

@pytest.fixture()
def file_name():
    return PDF_FILE_NAME

@pytest.fixture()
def delete_files_regex_string():
    return DOWNLOADED_PDF_REGEX

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

@pytest.mark.headed
def test_download_pdf_data(
    driver: Firefox,
    fillable_pdf_url: str,
    downloads_folder: str,
    file_name,
    delete_files,
    delete_files_regex_string,
):
    """
    C1020327: Sangie/Verify that a PDF with filled data is successfully downloaded in Private window
    """

    # Open Private Window
    panel = PanelUi(driver)
    panel.open_and_switch_to_new_window("private")

    pdf_viewer = GenericPdf(driver, pdf_url=fillable_pdf_url)
    pdf_viewer.open()
    pdf_viewer.fill_element("first-name-field", "John")

    # Finally download the edited pdf
    pdf_viewer.click_download_button()
    time.sleep(2)
    pdf_viewer.handle_os_download_confirmation()

    # Set the expected download path and the expected PDF name
    saved_pdf_location = os.path.join(downloads_folder, file_name)
    _wait_for_file_download(saved_pdf_location)

    # Verify if the file exists
    assert os.path.exists(saved_pdf_location), (
        f"The file was not downloaded to {saved_pdf_location}."
    )