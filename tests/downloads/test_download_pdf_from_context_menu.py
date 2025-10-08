from time import sleep

import pytest
from pynput.keyboard import Controller
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import ContextMenu
from modules.browser_object_tabbar import TabBar
from modules.page_object import AboutTelemetry, GenericPdf


@pytest.fixture()
def test_case():
    return "1756790"


@pytest.fixture()
def delete_files_regex_string():
    return r".*i-9.pdf"


PDF_TELEMETRY_DATA = ["downloads", "added", "fileExtension", "pdf"]


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

    # Initialize objects
    pdf = GenericPdf(driver, pdf_url=fillable_pdf_url)
    context_menu = ContextMenu(driver)
    about_telemetry = AboutTelemetry(driver)
    tabs = TabBar(driver)

    # Right-click on the body of the file and select Save page as
    pdf.open()
    body = pdf.get_element("pdf-body")
    pdf.context_click(body)
    context_menu.click_and_hide_menu("context-menu-save-page-as")

    # Allow time for the save dialog to appear and handle prompt
    sleep(2)
    context_menu.hide_popup_by_child_node("context-menu-save-page-as")
    keyboard = Controller()
    pdf.handle_os_download_confirmation(keyboard, sys_platform)

    # Allow time for the download to complete
    sleep(3)

    # Open about:telemetry in a new tab and go to the Events tab
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    about_telemetry.open()
    about_telemetry.click_on("events-tab")

    # Verify telemetry
    all_rows = driver.find_elements(By.CSS_SELECTOR, "#events-section table tr")

    pdf_telemetry_row = None
    for row in reversed(all_rows):
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) > 1:
            cell_texts = [cell.text.strip() for cell in cells[1:]]
            if cell_texts == PDF_TELEMETRY_DATA:
                pdf_telemetry_row = cells
                break

    assert pdf_telemetry_row is not None, "PDF telemetry data not found in events table"
    cell_texts = [cell.text.strip() for cell in pdf_telemetry_row[1:]]
    assert PDF_TELEMETRY_DATA == cell_texts
