import os
import shutil

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_context_menu import ContextMenu
from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "1756743"


ZIP_URL = "https://github.com/microsoft/api-guidelines"
ANGLE_BRACKET_SVG_PATH = "m11.28 3.22 4.25 4.25a.75.75 0 0 1 0 1.06l-4.25 4.25a.749.749 0 0 1-1.275-.326.749.749 0 0 1 .215-.734L13.94 8l-3.72-3.72a.749.749 0 0 1 .326-1.275.749.749 0 0 1 .734.215Zm-6.56 0a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042L2.06 8l3.72 3.72a.749.749 0 0 1-.326 1.275.749.749 0 0 1-.734-.215L.47 8.53a.75.75 0 0 1 0-1.06Z"


@pytest.fixture()
def delete_files_regex_string():
    return r"api-guidelines-vNext"


@pytest.fixture()
def temp_selectors():
    return {
        "github-code-button": {
            "selectorData": "/html/body/div[1]/div[4]/div/main/turbo-frame/div/div/div/div/div[1]/react-partial/div/div/div[2]/div[2]/button",
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
    driver: Firefox, sys_platform, home_folder, delete_files, temp_selectors
):
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
    web_page.click_on("github-code-button")
    web_page.click_on("github-download-button")

    # In the download panel right-click on the download and click "Always Open Similar Files"
    with driver.context(driver.CONTEXT_CHROME):
        nav.context_click(nav.get_element("download-panel-item"))
        context_menu.get_element("context-menu-always-open-similar-files").click()

    # Open about:preferences and check that zip mime type is present in the application list
    about_prefs.open()
    about_prefs.element_exists("mime-type-item", labels=["application/zip"])

    # Remove the directory created as MacOS automatically unzips
    if sys_platform == "Darwin":
        dir_created = os.path.join(home_folder, "Downloads", "api-guidelines-vNext")
        shutil.rmtree(dir_created)
