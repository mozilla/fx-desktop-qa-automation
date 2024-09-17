import pytest
import shutil
import os
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

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

def test_add_zip_type(driver: Firefox, sys_platform, home_folder, delete_files):
    """
    C1756743: Verify that the user can add the .zip mime type to Firefox
    """
    # instantiate object
    web_page = GenericPage(driver, url=ZIP_URL).open()
    nav = Navigation(driver)
    context_menu = ContextMenu(driver)
    about_prefs = AboutPrefs(driver, category="general")

    # Click on the available zip
    web_page.find_element(
        By.XPATH, '//*[@id=":R55ab:"]'
    ).click()
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.Overlay__StyledOverlay-sc-51280t-0 > div:nth-child(2)')))
    web_page.find_element(
        By.CSS_SELECTOR, 'li.Item__LiBox-sc-yeql7o-0:nth-child(2)'
    ).click()

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
