import os
import time

import pytest
from pynput.keyboard import Controller
from selenium.webdriver import Firefox

from modules.page_object import GenericPdf


@pytest.fixture()
def test_case():
    return "1756769"


@pytest.fixture()
def delete_files_regex_string():
    return r".*i-9.pdf"


@pytest.mark.headed
def test_download_pdf(
    driver: Firefox,
    fillable_pdf_url: str,
    downloads_folder: str,
    sys_platform,
    delete_files,
):
    """
    C1756769: Verify that the user can Download a PDF

    Notes:
        - Firefox is launched with a new profile that has default download settings.
        - This means the OS-level "Save File" dialog will appear for every download.
        - Selenium cannot interact with this native dialog directly, so the test
          must rely on fixed waits to give the OS time to render the dialog and to
          finish writing the file.
    """

    # Initialize objects
    pdf = GenericPdf(driver, pdf_url=fillable_pdf_url)
    keyboard = Controller()

    # Click the download button
    pdf.open()
    download_button = pdf.get_element("download-button")
    download_button.click()

    # Allow time for the download dialog to appear and pressing handle the prompt
    time.sleep(2)
    pdf.handle_os_download_confirmation(keyboard, sys_platform)

    # Set the expected download path and the expected PDF name
    file_name = "i-9.pdf"
    saved_pdf_location = os.path.join(downloads_folder, file_name)

    # Wait up to 10 seconds for the file to appear and finish downloading
    timeout = 10
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(saved_pdf_location):
            break
        time.sleep(0.5)

    # Verify that the file was downloaded
    assert os.path.exists(saved_pdf_location), (
        f"The file was not downloaded to {saved_pdf_location} after {timeout} seconds."
    )
