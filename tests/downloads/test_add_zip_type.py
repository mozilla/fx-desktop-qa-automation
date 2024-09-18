import pytest
import shutil
import os
from selenium.webdriver import Firefox

from modules.browser_object_context_menu import ContextMenu
from modules.browser_object_navigation import Navigation
from modules.page_object_about_prefs import AboutPrefs
from modules.page_object_generics import GenericPage


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
        'github-code-button': {
            'selectorData': ':R55ab:',
            'strategy': 'id',
            'groups': []
        },
        'github-download-button': {
            'selectorData': 'a[href="/microsoft/api-guidelines/archive/refs/heads/vNext.zip"]',
            'strategy': 'css',
            'groups': []
        }
    }

def test_add_zip_type(driver: Firefox, sys_platform, home_folder, delete_files, temp_selectors):
    """
    C1756743: Verify that the user can add the .zip mime type to Firefox
    """
    # instantiate object
    web_page = GenericPage(driver, url=ZIP_URL).open()
    nav = Navigation(driver)
    context_menu = ContextMenu(driver)
    about_prefs = AboutPrefs(driver, category="general")

    web_page.elements |= temp_selectors

    # Click on the available zip
    web_page.click_on('github-code-button')
    web_page.click_on('github-download-button')

    # In the download panel right-click on the download and click "Always Open Similar Files"
    with driver.context(driver.CONTEXT_CHROME):
        nav.context_click(nav.get_element("download-panel-item"))
        context_menu.get_element("context-menu-always-open-similar-files").click()

    # Open about:preferences and check that zip mime type is present in the application list
    about_prefs.open()
    about_prefs.element_exists("mime-type", labels=["application/zip"])

    # Remove the directory created as MacOS automatically unzips
    if sys_platform == "Darwin":
        dir_created = os.path.join(home_folder, "Downloads", "api-guidelines-vNext")
        shutil.rmtree(dir_created)
