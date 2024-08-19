from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object_context_menu import ContextMenu
from modules.browser_object_navigation import Navigation
from modules.page_object_about_prefs import AboutPrefs
from modules.page_object_generics import GenericPage

ZIP_URL = "https://ftp.mozilla.org/pub/firefox/releases/0.9rc/"


def test_add_zip_type(driver: Firefox):
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
        By.XPATH, "//td/a[@href='/pub/firefox/releases/0.9rc/Firefox-win32-0.9rc.zip']"
    ).click()

    # In the download panel right-click on the download and click "Always Open Similar Files"
    with driver.context(driver.CONTEXT_CHROME):
        nav.context_click(nav.get_element("download-panel-item"))
        context_menu.get_element("context-menu-always-open-similar-files").click()

    # Open about:preferences and check that zip mime type is present in the application list
    about_prefs.open()
    about_prefs.element_exists("mime-type", labels=["application/zip"])
