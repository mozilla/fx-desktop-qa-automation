from time import sleep
import os
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.page_object_generics import GenericPdf


@pytest.fixture()
def delete_files_regex_string():
    return r"i-9.*\.pdf"


@pytest.mark.headed
@pytest.mark.unstable
def test_download_pdf_with_form_fields(
        driver: Firefox,
        fillable_pdf_url: str,
        downloads_folder: str,
        sys_platform,
        delete_files,
):
    """
    C1020326 Download pdf with form fields
    """
    from pynput.keyboard import Controller, Key

    pdf_page = GenericPdf(driver, pdf_url=fillable_pdf_url).open()
    keyboard = Controller()

    # Fill in the name field and click on download button
    pdf_page.get_element("first-name-field").send_keys("Mark")
    pdf_page.get_element("download-button").click()

    # Allow time for the download dialog to appear and press enter to download
    sleep(2)

    if sys_platform == "Linux":
        keyboard.press(Key.alt)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        keyboard.release(Key.alt)
        sleep(1)
        keyboard.press(Key.alt)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        keyboard.release(Key.alt)
        sleep(1)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        sleep(1)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)

    # Allow time for the download to complete
    sleep(2)

    # Set the expected download path and the expected PDF name
    file_name = "i-9.pdf"
    saved_pdf_location = os.path.join(downloads_folder, file_name)

    # Verify if the file exists
    assert os.path.exists(
        saved_pdf_location
    ), f"The file was not downloaded to {saved_pdf_location}."

    # Open the saved pdf and check if the edited field is displayed
    driver.get("file://" + os.path.realpath(saved_pdf_location))
    assert pdf_page.get_element("edited-name-field").is_displayed()