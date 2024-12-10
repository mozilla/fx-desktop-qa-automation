import os
import time

import pytest
from selenium.webdriver import Firefox

from modules.page_object import GenericPdf


@pytest.fixture()
def test_case():
    return "3932"


@pytest.fixture()
def add_prefs():
    return []


@pytest.fixture()
def delete_files_regex_string():
    return r"i-9.*\.pdf"


@pytest.mark.headed
def test_pdf_download(
    driver: Firefox,
    fillable_pdf_url: str,
    downloads_folder: str,
    sys_platform,
    delete_files,
):
    """
    C3932: PDF files can be successfully downloaded via pdf.js
    """
    from pynput.keyboard import Controller

    pdf = GenericPdf(driver, pdf_url=fillable_pdf_url)
    pdf.open()
    keyboard = Controller()

    # Click the download button
    pdf.get_element("download-button").click()

    # Allow time for the download dialog m to appear and pressing enter to download
    time.sleep(2)
    pdf.handle_os_download_confirmation(keyboard, sys_platform)

    # Set the expected download path and the expected PDF name
    file_name = "i-9.pdf"
    saved_pdf_location = os.path.join(downloads_folder, file_name)
    pdf.expect(lambda _: os.path.exists(saved_pdf_location))

    # Verify if the file exists
    assert os.path.exists(
        saved_pdf_location
    ), f"The file was not downloaded to {saved_pdf_location}."

    print(
        f"Test passed: The file {file_name} has been downloaded and is present at {saved_pdf_location}."
    )
    driver.quit()
