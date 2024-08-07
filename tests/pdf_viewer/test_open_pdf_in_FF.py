import os
import time

import pytest
from selenium.webdriver import Firefox

from modules.page_object import GenericPdf


@pytest.fixture()
def add_prefs():
    return []


@pytest.mark.headed
def test_open_pdf_in_ff(
    driver: Firefox, fillable_pdf_url: str, downloads_folder: str, sys_platform
):
    """
    C936503: PDF files can be successfully opened in Firefox
    """
    from pynput.keyboard import Controller, Key

    pdf = GenericPdf(driver, pdf_url=fillable_pdf_url).open()
    keyboard = Controller()

    # Click the download button
    download_button = pdf.get_element("download-button")
    download_button.click()

    # Allow time for the download dialog m to appear and pressing enter to download
    time.sleep(2)

    if sys_platform == "Linux":
        keyboard.press(Key.alt)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        keyboard.release(Key.alt)
        time.sleep(1)
        keyboard.press(Key.alt)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        keyboard.release(Key.alt)
        time.sleep(1)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        time.sleep(1)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)

    keyboard.press(Key.enter)
    keyboard.release(Key.enter)

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

    file_url = f"file://{saved_pdf_location}"
    driver.get(file_url)

    # Allow time for the PDF to load
    time.sleep(5)

    # Verify that the PDF viewer is loaded
    assert "pdf" in driver.current_url, "The PDF viewer did not load correctly."
    assert "i-9.pdf" in driver.title, "The PDF file did not open correctly."
    print(
        f"Test passed: The PDF file {file_name} has been opened correctly in Firefox."
    )
    driver.quit()
