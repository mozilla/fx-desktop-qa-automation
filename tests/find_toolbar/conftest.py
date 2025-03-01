import pytest
from selenium.webdriver import Firefox

from modules.browser_object_find_toolbar import FindToolbar
from modules.util import BrowserActions


@pytest.fixture()
def suite_id():
    return ("2085", "Find Toolbar")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []


@pytest.fixture()
def find_toolbar(driver: Firefox):
    find_toolbar = FindToolbar(driver)
    yield find_toolbar


@pytest.fixture()
def browser_actions(driver: Firefox):
    ba = BrowserActions(driver)
    yield ba
