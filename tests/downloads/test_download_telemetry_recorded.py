import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_about_pages import AboutTelemetry
from modules.page_object_generics import GenericPage

TEST_URL = "https://ash-speed.hetzner.com/"
DOWNLOADS_TELEMETRY_DATA = ["downloads", "added", "fileExtension", "bin"]


@pytest.fixture()
def delete_files_regex_string():
    return r"100MB.BIN"


@pytest.fixture()
def test_case():
    return "1756775"


def test_download_telemetry_recorded(driver: Firefox):
    """
    C1756775 - Verify that Telemetry is recorded for Downloading a file
    """

    # Instantiate objects
    page = GenericPage(driver, url=TEST_URL)
    telemetry = AboutTelemetry(driver)
    nav = Navigation(driver)

    # Open test url and download a file
    page.open()
    page.click_on("sample-bin-download-100mb")

    # Wait for download completion
    nav.wait_for_download_animation_finish()

    # Open about:telemetry and go to the Events tab
    telemetry.open()
    telemetry.click_on("events-tab")

    # Verify telemetry
    assert telemetry.is_telemetry_events_entry_present(DOWNLOADS_TELEMETRY_DATA)
