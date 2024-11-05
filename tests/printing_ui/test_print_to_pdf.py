import os
from time import sleep

import pytest
from pynput.keyboard import Controller
from selenium.webdriver import Firefox

from modules.browser_object_panel_ui import PanelUi
from modules.page_object_generics import GenericPdf


@pytest.fixture()
def test_case():
    return "965142"


@pytest.fixture()
def delete_files_regex_string():
    return r".*wikipedia.pdf"


@pytest.fixture()
def set_prefs():
    return [("print.always_print_silent", True)]


TEST_PAGE = "https://en.wikipedia.org"


@pytest.mark.headed
def test_print_to_pdf(
    driver: Firefox,
    downloads_folder: str,
    sys_platform,
    delete_files,
):
    """
    C965142 - Verify that the user can print a webpage to PDF
    """

    keyboard = Controller()
    panel_ui = PanelUi(driver)
    pdf = GenericPdf(driver)

    driver.get(TEST_PAGE)

    # Select Print option from Hamburger Menu in order to trigger the silent printing
    with driver.context(driver.CONTEXT_CHROME):
        panel_ui.open_panel_menu()
        panel_ui.select_panel_setting("print-option")

    # Allow time for the Save As dialog to appear
    sleep(5)

    # Type a file name in the native dialog and save the PDF
    keyboard.type("wikipedia.pdf")
    pdf.handle_os_download_confirmation(keyboard, sys_platform)

    # Set the expected download path and the expected PDF name
    expected_file_name = "wikipedia.pdf"
    saved_pdf_location = os.path.join(downloads_folder, expected_file_name)

    # Allow time for the file to be saved
    sleep(3)

    # Verify if the PDF file was saved in the downloads folder
    assert os.path.exists(
        saved_pdf_location
    ), f"The file was not downloaded to {saved_pdf_location}."

    print(
        f"Test passed: The file {expected_file_name} has been downloaded and is present at {saved_pdf_location}."
    )

    driver.quit()
