import os

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi, TabBar
from modules.page_object import GenericPdf


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


@pytest.fixture()
def add_to_prefs_list():
    return [
        # Suppress the Firefox 150+ private-browsing download notification dialog.
        ("browser.download.enableDeletePrivate", False),
        # Unsaved PDF edits otherwise raise a save prompt that blocks driver.quit().
        ("dom.disable_beforeunload", True),
    ]


@pytest.mark.headed
def test_download_pdf_data(
    driver: Firefox,
    pdf_file_path,
    downloads_folder: str,
    file_name,
    delete_files,
    delete_files_regex_string,
    wait_for_file_download,
):
    """
    C1020327: Verify that a PDF with filled data is successfully downloaded in Private window
    """

    # Open Private Window
    panel = PanelUi(driver)
    saved_pdf_location = os.path.join(downloads_folder, file_name)
    tabs = TabBar(driver)

    panel.open_and_switch_to_new_window("private")

    pdf_viewer = GenericPdf(driver, pdf_url=f"file://{pdf_file_path}")
    pdf_viewer.fill_element("first-name-field", "Mark")

    # The native "Save As" panel cannot be driven reliably by desktop input on any
    # platform, so mock the picker instead of clicking through it.
    pdf_viewer.install_mock_file_picker(saved_pdf_location)

    # Click the download button
    try:
        pdf_viewer.click_download_button()
        pdf_viewer.wait_for_mock_file_picker()
    finally:
        pdf_viewer.cleanup_mock_file_picker()

    # Wait for file download to complete
    wait_for_file_download(saved_pdf_location)

    # Open the saved pdf and check if the edited field is displayed
    tabs.open_and_switch_to_new_tab()
    driver.get("file://" + os.path.realpath(saved_pdf_location))
    pdf_viewer.element_visible("edited-name-field")

    # Verify if the file exists
    assert os.path.exists(saved_pdf_location), (
        f"The file was not downloaded to {saved_pdf_location}."
    )
