import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs

ZIP_URL = "https://github.com/microsoft/api-guidelines"


@pytest.fixture()
def test_case():
    return "1756743"


@pytest.fixture()
def delete_files_regex_string():
    return r"api-guidelines-vNext"


@pytest.fixture()
def temp_selectors():
    return {
        "github-code-button": {
            "strategy": "xpath",
            "selectorData": "//button[.//span[normalize-space()='Code']]",
            "groups": [],
        },
        "github-download-button": {
            "selectorData": 'a[href="/microsoft/api-guidelines/archive/refs/heads/vNext.zip"]',
            "strategy": "css",
            "groups": [],
        },
    }


def test_add_zip_type(
    driver: Firefox,
    sys_platform,
    home_folder,
    delete_files,
    temp_selectors,
    close_file_manager,
):
    """
    C1756743: Verify that the user can add the .zip mime type to Firefox
    """
    # Instantiate objects
    web_page = GenericPage(driver, url=ZIP_URL)
    nav = Navigation(driver)
    about_prefs = AboutPrefs(driver, category="general")

    # Add temporary selectors for GitHub UI
    web_page.elements |= temp_selectors

    # Trigger a ZIP download from GitHub
    web_page.open()
    web_page.click_on("github-code-button")
    web_page.click_on("github-download-button")

    # In the download panel right-click on the download and click "Always Open Similar Files"
    nav.perform_download_context_action("context-menu-always-open-similar-files")

    # Open about:preferences and verify ZIP mime type is present
    about_prefs.open()
    assert about_prefs.get_app_name_for_mime_type("application/zip"), (
        "ZIP mime type not found in Applications list"
    )
