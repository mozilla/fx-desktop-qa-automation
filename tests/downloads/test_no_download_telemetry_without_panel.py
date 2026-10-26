import pytest
from selenium.webdriver import Firefox

from modules.page_object_about_pages import AboutTelemetry
from modules.page_object_generics import GenericPage

# Link page, since opening the file directly hangs driver.get
TEST_URL = (
    'data:text/html,<a href="https://filesamples.com/samples/document/doc/sample2.doc">'
    "sample2.doc</a>"
)
DOWNLOADS_TELEMETRY_DATA = ["downloads.panel_shown"]


@pytest.fixture()
def delete_files_regex_string():
    return r"sample2.doc"


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

    # Open test url and download a file
    page.open()
    page.click_on("sample-doc-download")

    # Open about:telemetry and go to the Events tab
    telemetry.open()
    telemetry.click_on("scalars-tab")

    # Verify telemetry
    assert not telemetry.is_telemetry_scalars_entry_present(DOWNLOADS_TELEMETRY_DATA)
