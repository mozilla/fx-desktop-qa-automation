import pytest
from selenium.webdriver import Firefox

from modules.browser_object import FindToolbar


def test_find_toolbar_search(driver: Firefox):
    driver.get("about:about")
    find_toolbar = FindToolbar(driver).open()
    find_toolbar.find("teleme")
