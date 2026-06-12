import os
import time

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.browser_object import TabBar
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
    # Suppress the Firefox 150+ private-browsing download notification dialog.
    return [("browser.download.enableDeletePrivate", False)]


@pytest.fixture()
def hard_quit():
    # Skip the graceful driver.quit(); gracefully closing the private window
    # with the edited PDF still open re-raises a native save/cancel prompt.
    return True


@pytest.mark.headed
def test_download_pdf_data(
    driver: Firefox,
    pdf_file_path,
    downloads_folder: str,
    sys_platform,
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

    use_mock_picker = sys_platform == "Linux"
    if use_mock_picker:
        pdf_viewer.install_mock_file_picker(saved_pdf_location)

    # Click the download button
    try:
        pdf_viewer.click_download_button()

        if use_mock_picker:
            pdf_viewer.wait_for_mock_file_picker()
        else:
            # Allow time for the download dialog to appear and pressing enter to download
            time.sleep(2)

            # Handle OS download prompt
            pdf_viewer.handle_os_download_confirmation()
    finally:
        if use_mock_picker:
            pdf_viewer.cleanup_mock_file_picker()

    # # Set the expected download path and the expected PDF name
    wait_for_file_download(saved_pdf_location)

    # Open the saved pdf and check if the edited field is displayed
    tabs.open_and_switch_to_new_tab()
    driver.get("file://" + os.path.realpath(saved_pdf_location))
    pdf_viewer.element_visible("edited-name-field")

    # Verify if the file exists
    assert os.path.exists(saved_pdf_location), (
        f"The file was not downloaded to {saved_pdf_location}."
    )
