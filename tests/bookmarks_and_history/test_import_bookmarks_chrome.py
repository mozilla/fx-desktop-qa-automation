from time import sleep
from selenium.webdriver import (Firefox, Chrome, ActionChains)
from selenium.webdriver.common.keys import Keys
from modules.page_object import AboutPrefs

import pytest

TEST_SITE = "https://www.example.com"

@pytest.fixture()
def test_case():
    return "2084639"

@pytest.fixture()
def chrome_bookmarks():
    def _chrome_bookmarks():
        chrome = Chrome()
        chrome.get(TEST_SITE)
        actions = ActionChains(chrome)
        actions.key_down(Keys.COMMAND).send_keys('d').key_up(Keys.COMMAND).perform()
        sleep(2)
    return _chrome_bookmarks

def test_chrome_bookmarks_imported(chrome_bookmarks, driver: Firefox):
    chrome_bookmarks()
    about_prefs = AboutPrefs(driver, category="General")
    about_prefs.open()
    about_prefs.click_on("import-browser-data")
    about_prefs.import_bookmarks("Chrome")
    toolbar = Toolbar(driver)
    toolbar.confirm_bookmark_exists(TEST_SITE)
