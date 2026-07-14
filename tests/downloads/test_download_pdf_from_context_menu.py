import os

import pytest
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
    delete_files,
    wait_for_file_download,
):
    """
    C1756790: Verify that Telemetry is recorded when Saving a PDF from the Context menu

    Notes:
        - The native "Save File" picker is mocked on all platforms so the
          download runs headlessly in CI. Driving the OS file dialog is
          unreliable there (Linux Wayland cannot drive GTK pickers through
          desktop input, and Windows image-matching depends on the CI
          resolution/DPI/theme).
    """

    # Set the expected download path and the expected PDF name
    file_name = "i-9.pdf"
    saved_pdf_location = os.path.join(downloads_folder, file_name)

    # Initialize objects
    pdf_page = GenericPdf(driver, pdf_url=fillable_pdf_url)
    context_menu = ContextMenu(driver)
    about_telemetry = AboutTelemetry(driver)
    tabs = TabBar(driver)
    nav = Navigation(driver)

    # Replace the native save dialog with a mock that returns our target path
    pdf_page.install_mock_file_picker(saved_pdf_location)
    try:
        # Right-click on the body of the file and select Save page as
        body = pdf_page.get_element("pdf-body")
        pdf_page.context_click(body)
        context_menu.click_and_hide_menu("context-menu-save-page-as")
        pdf_page.wait_for_mock_file_picker()
    finally:
        pdf_page.cleanup_mock_file_picker()

    # Allow the download to complete
    nav.wait_for_download_animation_finish()
    assert wait_for_file_download(saved_pdf_location), (
        f"File not found: {saved_pdf_location}"
    )

    # Open about:telemetry in a new tab and go to the Events tab
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    about_telemetry.open()
    about_telemetry.click_on("events-tab")

    # Verify telemetry
    assert about_telemetry.is_telemetry_events_entry_present(PDF_TELEMETRY_DATA)
