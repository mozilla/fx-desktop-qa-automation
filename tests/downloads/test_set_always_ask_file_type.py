from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation
from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "1756752"


@pytest.fixture()
def delete_files_regex_string():
    return r"pdf-example-bookmarks.pdf"


CONTENT_DISPOSITION_ATTACHMENT_URL = (
    "https://download.novapdf.com/download/samples/pdf-example-bookmarks.pdf"
)


@pytest.mark.ci
def test_set_always_ask_file_type(driver: Firefox, delete_files):
    """
    C1756752: Ensure that the Always ask option in Firefox Applications settings
    leads to a dialog asking "What should Firefox do with this file?" when the file type
    is downloaded.
    """
    nav = Navigation(driver)
    about_prefs = AboutPrefs(driver, category="general").open()

    about_prefs.click_on("pdf-content-type")
    about_prefs.click_on("pdf-actions-menu")
    menu = about_prefs.get_element("pdf-actions-menu")
    menu.send_keys(Keys.DOWN)
    menu.send_keys(Keys.ENTER)

    nav.search(CONTENT_DISPOSITION_ATTACHMENT_URL)
    sleep(2)
    with driver.context(driver.CONTEXT_CHROME):
        driver.switch_to.window(driver.window_handles[-1])
        driver.find_element(By.ID, "unknownContentTypeWindow").send_keys(Keys.ESCAPE)
