import os
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.page_object_generics import GenericPdf


@pytest.fixture()
def test_case():
    return "1020326"


@pytest.fixture()
def delete_files_regex_string():
    return r"i-9.*\.pdf"


@pytest.mark.headed
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
    from pynput.keyboard import Controller

    pdf_page = GenericPdf(driver, pdf_url=fillable_pdf_url).open()
    keyboard = Controller()

    # Fill in the name field and click on download button
    pdf_page.get_element("first-name-field").send_keys("Mark")
    pdf_page.get_element("download-button").click()

    # Allow time for the download dialog to appear and handle the prompt
    sleep(2)
    pdf_page.handle_os_download_confirmation(keyboard, sys_platform)

    # Allow time for the download to complete
    sleep(3)

    # Set the expected download path and the expected PDF name
    file_name = "i-9.pdf"
    saved_pdf_location = os.path.join(downloads_folder, file_name)

    # Verify if the file exists
    assert os.path.exists(saved_pdf_location), (
        f"The file was not downloaded to {saved_pdf_location}."
    )

    # Open the saved pdf and check if the edited field is displayed
    driver.get("file://" + os.path.realpath(saved_pdf_location))

    pdf_page.element_visible("edited-name-field")
