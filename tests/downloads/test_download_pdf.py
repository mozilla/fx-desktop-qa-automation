import os
import time

import pytest
from selenium.webdriver import Firefox

from modules.page_object import GenericPdf


@pytest.fixture()
def test_case():
    return "1756769"


@pytest.fixture()
def delete_files_regex_string():
    return r".*i-9.pdf"


def wait_for_file_download(file_path, timeout=10, interval=0.5):
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(file_path):
            return True
        time.sleep(interval)
    return False


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
    pdf_page = GenericPdf(driver, pdf_url=fillable_pdf_url)

    # Click the download button
    pdf_page.open()
    pdf_page.click_download_button()

    # Allow time for the download dialog to appear and pressing handle the prompt
    time.sleep(2)
    pdf_page.handle_os_download_confirmation()

    # Set the expected download path and the expected PDF name
    file_name = "i-9.pdf"
    saved_pdf_location = os.path.join(downloads_folder, file_name)

    # Wait up to 10 seconds for the file to appear and finish downloading
    assert wait_for_file_download(saved_pdf_location, timeout=10), (
        f"File not found: {saved_pdf_location}"
    )
