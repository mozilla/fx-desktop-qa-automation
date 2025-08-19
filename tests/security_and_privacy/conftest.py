import pytest

from modules.browser_object_navigation import Navigation
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def suite_id():
    return ("5833", "Security and Privacy")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = [("browser.urlbar.scotchBonnet.enableOverride", True)]
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []


@pytest.fixture()
def nav(driver):
    return Navigation(driver)


@pytest.fixture()
def about_prefs_privacy(driver):
    return AboutPrefs(driver, category="privacy")
