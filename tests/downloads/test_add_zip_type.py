import os
import shutil

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "1756743"


ZIP_URL = "https://github.com/microsoft/api-guidelines"


@pytest.fixture()
def delete_files_regex_string():
    return r"api-guidelines-vNext"


@pytest.fixture()
def temp_selectors():
    return {
        "github-code-button": {
            "selectorData": "//span[@class='prc-Button-Label-pTQ3x' and text()='Code']",
            "strategy": "xpath",
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

    web_page.elements |= temp_selectors

    # Click on the available zip
    web_page.open()
    web_page.click_on("github-code-button")
    web_page.click_on("github-download-button")

    # In the download panel right-click on the download and click "Always Open Similar Files"
    nav.perform_download_context_action("context-menu-always-open-similar-files")

    # Open about:preferences and check that zip mime type is present in the application list
    about_prefs.open()
    about_prefs.get_app_name_for_mime_type("application/zip")

    # Remove the directory created as macOS automatically unzips
    if sys_platform == "Darwin":
        dir_created = os.path.join(home_folder, "Downloads", "api-guidelines-vNext")
        shutil.rmtree(dir_created)
