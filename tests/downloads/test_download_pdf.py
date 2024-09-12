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
    """
    from pynput.keyboard import Controller, Key

    pdf = GenericPdf(driver, pdf_url=fillable_pdf_url).open()
    keyboard = Controller()

    # Click the download button
    download_button = pdf.get_element("download-button")
    download_button.click()

    # Allow time for the download dialog to appear and pressing handle the prompt
    time.sleep(2)
    pdf.handle_os_download_confirmation(keyboard, sys_platform)

    # Allow time for the download to complete
    time.sleep(2)

    # Set the expected download path and the expected PDF name
    file_name = "i-9.pdf"
    saved_pdf_location = os.path.join(downloads_folder, file_name)

    # Verify if the file exists
    assert os.path.exists(
        saved_pdf_location
    ), f"The file was not downloaded to {saved_pdf_location}."

    print(
        f"Test passed: The file {file_name} has been downloaded and is present at {saved_pdf_location}."
    )
    driver.quit()
