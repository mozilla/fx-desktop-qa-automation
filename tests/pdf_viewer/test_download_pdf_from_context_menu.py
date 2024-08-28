import platform
from time import sleep

import pytest
from selenium.webdriver import ActionChains, Firefox
from selenium.webdriver.common.by import By

from modules.page_object import AboutTelemetry, GenericPdf


@pytest.fixture()
def delete_files_regex_string():
    return r".*i-9.pdf"


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

    from pynput.keyboard import Controller, Key

    pdf = GenericPdf(driver, pdf_url=fillable_pdf_url).open()
    keyboard = Controller()
    action = ActionChains(driver)
    body = pdf.get_element("pdf-body")

    # Right-click on the body of the file and select Save page as
    action.context_click(body).perform()

    # Set the range based on the operating system
    current_os = platform.system()
    if current_os == "Windows":
        iterations = 3
    elif current_os == "Darwin":
        iterations = 3
    else:
        iterations = 3

    # Simulate pressing the down arrow to select the "Save As" option
    for _ in range(iterations):
        keyboard.press(Key.down)
        keyboard.release(Key.down)
        sleep(0.5)

    # Press Enter to confirm the "Save As" action
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)

    # Allow time for the save dialog to appear and press enter
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
    sleep(4)

    # Open about:telemetry and go to events tab
    about_telemetry = AboutTelemetry(driver).open()
    about_telemetry.get_element("events-tab").click()

    # Verify that Telemetry is recorded
    pdf_telemetry_data = ["downloads", "added", "fileExtension", "pdf"]
    last_rows = driver.find_elements(By.CSS_SELECTOR, '#events-section table tr:last-child td')
    # Extract the text from the last cell without the first column and store it
    cell_texts = [cell.text.strip() for cell in last_rows[1:]]
    assert pdf_telemetry_data == cell_texts
