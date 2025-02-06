from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import ContextMenu
from modules.page_object import AboutTelemetry, GenericPdf


@pytest.fixture()
def test_case():
    return "1756790"


@pytest.fixture()
def delete_files_regex_string():
    return r".*i-9.pdf"


@pytest.mark.unstable(reason="bug 1946131")
@pytest.mark.headed
def test_download_pdf_from_context_menu(
    driver: Firefox,
    fillable_pdf_url: str,
    downloads_folder: str,
    sys_platform,
    delete_files,
):
    """
    C1756790: Verify that Telemetry is Recorded when Saving a PDF from the Context menu
    """

    from pynput.keyboard import Controller

    pdf = GenericPdf(driver, pdf_url=fillable_pdf_url)
    pdf.open()
    keyboard = Controller()
    body = pdf.get_element("pdf-body")

    # Right-click on the body of the file and select Save page as
    pdf.context_click(body)
    context_menu = ContextMenu(driver)
    context_menu.click_and_hide_menu("context-menu-save-page-as")

    # Allow time for the save dialog to appear and handle prompt
    sleep(2)
    context_menu.hide_popup_by_child_node("context-menu-save-page-as")
    pdf.handle_os_download_confirmation(keyboard, sys_platform)

    # Allow time for the download to complete
    sleep(3)

    # Open about:telemetry and go to events tab
    about_telemetry = AboutTelemetry(driver).open()
    about_telemetry.get_element("events-tab").click()

    # Verify that Telemetry is recorded
    pdf_telemetry_data = ["downloads", "added", "fileExtension", "pdf"]

    if sys_platform == "Windows":
        # Use the second-to-last row on Windows
        pdf_telemetry_row = driver.find_elements(
            By.CSS_SELECTOR, "#events-section table tr:nth-last-child(2) td"
        )
    else:
        # Use the last row on other OSes
        pdf_telemetry_row = driver.find_elements(
            By.CSS_SELECTOR, "#events-section table tr:last-child td"
        )

    # Extract the text from the last cell without the first column and store it
    cell_texts = [cell.text.strip() for cell in pdf_telemetry_row[1:]]
    assert pdf_telemetry_data == cell_texts
