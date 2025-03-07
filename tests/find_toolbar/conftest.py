import pytest
from selenium.webdriver import Firefox

from modules.browser_object_find_toolbar import FindToolbar
from modules.util import BrowserActions


@pytest.fixture()
def suite_id():
    return ("2085", "Find Toolbar")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = []
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []


@pytest.fixture()
def find_toolbar(driver: Firefox):
    find_toolbar = FindToolbar(driver)
    yield find_toolbar


@pytest.fixture()
def browser_actions(driver: Firefox):
    ba = BrowserActions(driver)
    yield ba
