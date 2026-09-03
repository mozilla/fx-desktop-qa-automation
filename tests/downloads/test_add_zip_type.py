import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import AboutPrefs, GenericPage

ZIP_URL = "https://ftp.mozilla.org/pub/firefox/releases/0.9rc/"


@pytest.fixture()
def test_case():
    return "4108460"


@pytest.fixture()
def delete_files_regex_string():
    return r"Firefox-win32-0\.9rc.*\.zip"


@pytest.fixture()
def temp_selectors():
    return {
        "zip-download-link": {
            "selectorData": "a[href$='Firefox-win32-0.9rc.zip']",
            "strategy": "css",
            "groups": [],
        },
    }


@pytest.mark.headed
@pytest.mark.noxvfb
def test_add_zip_type(
    driver: Firefox, delete_files, temp_selectors, close_file_manager
):
    """
    C4108460 - Verify that downloading a .zip file adds the .zip MIME type
    entry to the Files and Applications list.
    """

    # Instantiate objects
    page = GenericPage(driver, url=ZIP_URL)
    nav = Navigation(driver)
    # The settings redesign (bug 2043378) moved file handlers to this pane
    about_prefs = AboutPrefs(driver, category="downloads")
    page.elements |= temp_selectors

    # Open the release directory listing and download the zip
    page.open()
    page.click_on("zip-download-link")

    # Download the file and set 'Always Open Similar Files'
    nav.perform_download_context_action("context-menu-always-open-similar-files")

    # Check the zip mime type is listed. Its label and app come from the OS
    about_prefs.open()
    about_prefs.element_exists("mime-type-item", labels=["application/zip"])
