from time import sleep

import pytest
from pynput.keyboard import Controller
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu
from modules.browser_object_navigation import Navigation
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
    C1756790: Verify that Telemetry is recorded when Saving a PDF from the Context menu

     Notes:
        - Firefox is launched with a new profile that has default download settings.
        - This means the OS-level "Save File" dialog will appear for every download.
        - Selenium cannot interact with this native dialog directly, so the test
          must rely on fixed waits to give the OS time to render the dialog and to
          finish writing the file.
    """

    # Initialize objects
    pdf_page = GenericPdf(driver, pdf_url=fillable_pdf_url)
    context_menu = ContextMenu(driver)
    about_telemetry = AboutTelemetry(driver)
    tabs = TabBar(driver)
    nav = Navigation(driver)

    # Right-click on the body of the file and select Save page as
    pdf_page.open()
    body = pdf_page.get_element("pdf-body")
    pdf_page.context_click(body)
    context_menu.click_and_hide_menu("context-menu-save-page-as")

    # Allow time for the save dialog to appear and handle prompt
    sleep(2)
    context_menu.hide_popup_by_child_node("context-menu-save-page-as")
    keyboard = Controller()
    pdf_page.handle_os_download_confirmation(keyboard, sys_platform)

    # Allow time for the download to complete
    nav.wait_for_download_animation_finish()

    # Open about:telemetry in a new tab and go to the Events tab
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    about_telemetry.open()
    about_telemetry.click_on("events-tab")

    # Verify telemetry
    assert about_telemetry.is_telemetry_events_entry_present(PDF_TELEMETRY_DATA)
