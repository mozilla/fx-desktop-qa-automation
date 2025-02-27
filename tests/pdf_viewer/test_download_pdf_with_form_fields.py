import os
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.page_object_generics import GenericPdf

PDF_FILE_NAME = "i-9.pdf"


@pytest.fixture()
def test_case():
    return "1020326"


@pytest.fixture()
def delete_files_regex_string():
    return r"i-9.*\.pdf"


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
):
    from pynput.keyboard import Controller

    """
    C1020326 Download pdf with form fields

    Arguments:
        sys_platform: Current System Platform Type
        pdf_viewer: instance of GenericPdf with correct path.
        downloads_folder: downloads folder path
        delete_files: fixture to remove the files after the test finishes
    """
    keyboard = Controller()

    # Fill in the name field and click on download button
    pdf_viewer.fill_element("first-name-field", "Mark")
    sleep(2)

    pdf_viewer.click_download_button()

    # Allow time for the download dialog to appear and handle the prompt
    sleep(2)
    pdf_viewer.handle_os_download_confirmation(keyboard, sys_platform)

    # Allow time for the download to complete
    sleep(3)

    # Set the expected download path and the expected PDF name
    saved_pdf_location = os.path.join(downloads_folder, PDF_FILE_NAME)

    # Verify if the file exists
    assert os.path.exists(saved_pdf_location), (
        f"The file was not downloaded to {saved_pdf_location}."
    )

    # Open the saved pdf and check if the edited field is displayed
    driver.get("file://" + os.path.realpath(saved_pdf_location))

    pdf_viewer.element_visible("edited-name-field")
