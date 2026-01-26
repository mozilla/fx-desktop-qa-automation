import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_about_pages import AboutTelemetry
from modules.page_object_generics import GenericPage

TEST_URL = "https://ash-speed.hetzner.com/"
DOWNLOADS_TELEMETRY_DATA = ["downloads.panel_shown"]


@pytest.fixture()
def delete_files_regex_string():
    return r"100MB.BIN"


@pytest.fixture()
def test_case():
    return "1756778"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.download.alwaysOpenPanel", False)]


def test_no_download_telemetry_without_panel(driver: Firefox):
    """
    C1756778 - Verify that no Telemetry is recorded if the Download panel never opens on downloads
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
    telemetry.click_on("scalars-tab")

    # Verify telemetry
    assert not telemetry.is_telemetry_entry_present(DOWNLOADS_TELEMETRY_DATA)
