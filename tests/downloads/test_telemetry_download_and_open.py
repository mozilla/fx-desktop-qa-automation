import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_about_pages import AboutTelemetry
from modules.page_object_generics import GenericPage

TEST_URL = "https://sapphire-hendrika-5.tiiny.site/"
OPEN_DOWNLOADS_TELEMETRY_DATA = ["downloads.file_opened", "1"]
REOPEN_DOWNLOADS_TELEMETRY_DATA = ["downloads.file_opened", "2"]


@pytest.fixture()
def delete_files_regex_string():
    return r"sample2.doc"


@pytest.fixture()
def test_case():
    return "1756776"


def test_telemetry_download_and_open(driver: Firefox):
    """
    C1756776 - Verify that telemetry is recorded when a user Downloads a file and opens it
    """

    # Instantiate objects
    page = GenericPage(driver, url=TEST_URL)
    telemetry = AboutTelemetry(driver)
    nav = Navigation(driver)

    # Open test url and download a file
    page.open()
    page.click_on("sample-doc-download")

    # Open the downloaded file
    nav.open_downloaded_file()

    # Open about:telemetry, select the scalars tab and search after "downloads.file_opened"
    telemetry.open()
    telemetry.click_on("scalars-tab")
    assert telemetry.is_telemetry_scalars_entry_present(OPEN_DOWNLOADS_TELEMETRY_DATA)

    # Redo the download with open
    page.open()
    page.click_on("sample-doc-download")

    # Open the downloaded file
    nav.open_downloaded_file()

    # Open about:telemetry, select the scalars tab and search after "downloads.file_opened"
    telemetry.open()
    telemetry.click_on("scalars-tab")
    assert telemetry.is_telemetry_scalars_entry_present(REOPEN_DOWNLOADS_TELEMETRY_DATA)
