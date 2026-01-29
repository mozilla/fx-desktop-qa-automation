import time
from asyncio import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_about_pages import AboutTelemetry
from modules.page_object_generics import GenericPage


TEST_URL = "https://sapphire-hendrika-5.tiiny.site/"
DOWNLOADS_PANEL_TELEMETRY_DATA = ["downloads.panel_shown", "1"]
DOWNLOADS_PANEL_TELEMETRY_DATA_RELOAD = ["downloads.panel_shown", "5"]
DOWNLOADS_PANEL_TELEMETRY_KEYED_SCALARS = ["downloads-button", "10"]


@pytest.fixture()
def delete_files_regex_string():
    return r"sample2.doc"


@pytest.fixture()
def test_case():
    return "1756777"


def test_verify_telemetry_downloads_panel_open(driver: Firefox):
    """
    C1756777 - Verify that telemetry is recorded for Opening the Downloads panel
    """

    # Instantiate objects
    page = GenericPage(driver, url=TEST_URL)
    telemetry = AboutTelemetry(driver)
    nav = Navigation(driver)

    # Open test url and download a file
    page.open()
    page.click_on("sample-doc-download")
    sleep(4)
    nav.open_downloads()
    sleep(1)
    nav.open_downloads()
    sleep(1)

    # Wait for download completion
    # nav.wait_for_download_animation_finish()
    nav.open_downloads()

    # Open about:telemetry and go to the Scalars tab
    telemetry.open()
    telemetry.click_on("scalars-tab")

    # Verify telemetry "downloads.panel_shown: 1"
    assert telemetry.is_telemetry_scalars_entry_present(DOWNLOADS_PANEL_TELEMETRY_DATA)

    # Open and dismiss the download panel 10 times
    for _ in range(10):
        nav.click_download_button()
        time.sleep(1)

    # Open about:telemetry and go to the Events tab
    telemetry.open()
    telemetry.click_on("scalars-tab")

    # Verify telemetry "downloads.panel_shown: 11"
    assert telemetry.is_telemetry_scalars_entry_present(DOWNLOADS_PANEL_TELEMETRY_DATA_RELOAD)

    # Open keyed scalars
    telemetry.click_on("scalars-tab")

    # Verify telemetry "downloads-button: 10"
    assert telemetry.is_telemetry_scalars_entry_present(DOWNLOADS_PANEL_TELEMETRY_KEYED_SCALARS)
