import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "1756722"


@pytest.fixture()
def delete_files_regex_string():
    return r"\bdownload\b"


MIXED_CONTENT_DOWNLOAD_URL = (
    "https://file-examples.com/wp-content/storage/2017/10/file-sample_100kB.odt"
)
MAX_CHECKS = 30


# This test has been found to be unstable in CI
def test_mixed_content_download_via_https(driver: Firefox, delete_files):
    """
    C1756722: Verify that the user can download mixed content via HTTPS
    """
    # Initialize objects
    web_page = GenericPage(driver, url=MIXED_CONTENT_DOWNLOAD_URL)
    nav = Navigation(driver)

    # Wait for the test website to wake up and download the content
    web_page.open()
    web_page.wait.until(lambda _: nav.element_visible("download-target-element"))

    # Verify download name matches expected pattern
    nav.verify_download_name(r"file-sample_100kB(\(\d+\))?.odt$")

    # Wait for download completion
    nav.wait_for_download_completion()
