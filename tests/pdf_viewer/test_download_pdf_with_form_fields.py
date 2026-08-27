import os

import pytest
from selenium.webdriver import Firefox

from modules.page_object_generics import GenericPdf

# The saved copy gets a unique name to avoid colliding with other i-9 downloads.
PDF_FILE_NAME = "i-9.pdf"
DOWNLOADED_PDF_NAME = "i-9-form-fields.pdf"
DOWNLOADED_PDF_REGEX = r"i-9-form-fields\.pdf"


@pytest.fixture()
def test_case():
    return "1020326"


@pytest.fixture()
def delete_files_regex_string():
    """Regex used by the cleanup fixture to remove downloaded files."""
    return DOWNLOADED_PDF_REGEX


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


@pytest.fixture()
def add_to_prefs_list():
    # Unsaved PDF edits otherwise raise a save prompt that blocks navigation.
    return [("dom.disable_beforeunload", True)]


@pytest.mark.headed
def test_download_pdf_with_form_fields(
    driver: Firefox,
    pdf_viewer: GenericPdf,
    delete_files,
    downloads_folder: str,
    delete_files_regex_string,
    wait_for_file_download,
):
    """
    C1020326 Download pdf with form fields

    Arguments:
        pdf_viewer: Fixture returning instance of GenericPdf with correct path.
        downloads_folder: Fixture returning downloads folder path
        delete_files: Fixture to remove the files after the test finishes
        wait_for_file_download: Fixture that blocks until the download completes
    """
    # Set the expected download path and the expected PDF name
    saved_pdf_path = os.path.join(downloads_folder, DOWNLOADED_PDF_NAME)

    # Fill in the name field
    pdf_viewer.fill_element("first-name-field", "Mark")

    # The native "Save As" panel cannot be driven reliably, so mock the picker.
    pdf_viewer.install_mock_file_picker(saved_pdf_path)

    # Trigger the download and confirm the save dialog opened
    try:
        pdf_viewer.click_download_button()
        pdf_viewer.wait_for_mock_file_picker()
    finally:
        pdf_viewer.cleanup_mock_file_picker()

    # Verify if the file exists
    wait_for_file_download(saved_pdf_path)

    # Open the saved pdf and check if the edited field is displayed
    driver.get("file://" + os.path.realpath(saved_pdf_path))
    pdf_viewer.element_visible("edited-name-field")
