import pytest
from selenium.webdriver import Firefox

from modules.page_object_about_pages import AboutTelemetry
from modules.page_object_generics import GenericPage

TEST_URL = "https://docs.google.com/document/d/1rEcPPWKnoUGFXHdxMDYrf5rcfK0h1yfLwR_a-dLfojA/edit?hl=en"
DOWNLOADS_PDF_TELEMETRY_DATA = ["downloads", "added", "fileExtension", "pdf"]


@pytest.fixture()
def delete_files_regex_string():
    return r"test CD_ attachment.pdf"


@pytest.fixture()
def test_case():
    return "1756779"


def test_telemetry_pdf_download_open(driver: Firefox):
    """
    C1756779 - Verify that the telemetry for the file extension is recorded when the user
     Downloads a PDF with open (gdoc/print pdf) (default)
    """

    # Instantiate objects
    page = GenericPage(driver, url=TEST_URL)
    telemetry = AboutTelemetry(driver)

    # Open gdoc and download as a pdf document
    page.open()
    page.download_gdoc_as_pdf()

    # Switch to first tab
    driver.switch_to.window(driver.window_handles[0])

    # Open about:telemetry and go to the Events tab
    telemetry.open()
    telemetry.click_on("events-tab")

    # Verify telemetry
    assert telemetry.is_telemetry_events_entry_present(DOWNLOADS_PDF_TELEMETRY_DATA)
