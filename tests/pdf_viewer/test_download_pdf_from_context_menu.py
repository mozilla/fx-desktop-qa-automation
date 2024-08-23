import platform
from time import sleep

import pytest
from selenium.webdriver import ActionChains, Firefox

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
        iterations = 1
    elif current_os == "Darwin":  # macOS is recognized as "Darwin"
        iterations = 3
    else:
        iterations = 1

    # Simulate pressing the down arrow to select the "Save As" option
    for _ in range(iterations):
        keyboard.press(Key.down)
        keyboard.release(Key.down)
        sleep(0.5)

    with driver.context(driver.CONTEXT_CHROME):
        driver.switch_to.window(driver.window_handles[-1])

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

    about_telemetry = AboutTelemetry(driver).open()
    sleep(5)

    about_telemetry.get_element("events-tab").click()
