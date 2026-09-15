import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "1756722"


MIXED_CONTENT_DOWNLOAD_URL = (
    "https://file-examples.com/wp-content/storage/2017/10/file-sample_100kB.odt"
)

# Firefox suffixes "(1)", "(2)"... when the file is already in the Downloads folder
DOWNLOAD_NAME_REGEX = r"file-sample_100kB(\(\d+\))?\.odt"


@pytest.fixture()
def delete_files_regex_string():
    """Delete the downloaded file, including any copies left by earlier runs."""
    return rf"{DOWNLOAD_NAME_REGEX}(\.part)?$"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.download.alwaysOpenPanel", True),
    ]


def test_mixed_content_download_via_https(driver: Firefox, delete_files):
    """
    C1756722: Verify that the user can download mixed content via HTTPS
    """
    # Initialize objects
    web_page = GenericPage(driver, url=MIXED_CONTENT_DOWNLOAD_URL)
    nav = Navigation(driver)

    # Open the page and trigger the mixed content download
    web_page.open()

    # Wait for the download entry to show up in the Downloads panel
    nav.wait_for_download_entry()

    # Verify download name matches expected pattern
    nav.verify_download_name(rf"{DOWNLOAD_NAME_REGEX}$")

    # Wait for download completion
    nav.wait_for_download_completion()
