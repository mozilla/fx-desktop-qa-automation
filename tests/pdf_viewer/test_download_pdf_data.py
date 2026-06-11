import os
import logging
import time
import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.page_object import GenericPdf
from modules.browser_object import PanelUi

@pytest.fixture()
def test_case():
    return "1020327"

PDF_FILE_NAME = "i-9.pdf"
DOWNLOADED_PDF_REGEX = r"i-9.*\.pdf"

@pytest.fixture()
def file_name():
    return PDF_FILE_NAME

@pytest.fixture()
def delete_files_regex_string():
    return DOWNLOADED_PDF_REGEX

def wait_for_file_download(file_path, timeout=10, interval=0.5):
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(file_path):
            return True
        time.sleep(interval)
    return False

def test_download_pdf_data(driver: Firefox, fillable_pdf_url: str, downloads_folder: str, file_name, delete_files):
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
    wait_for_file_download(saved_pdf_location)

    # Verify if the file exists
    assert os.path.exists(saved_pdf_location), (
        f"The file was not downloaded to {saved_pdf_location}."
    )



