import pytest
from selenium.webdriver import Firefox

from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def suite_id():
    # TODO: Replace with the actual TestRail suite number, e.g. ("12345", "AI Controls")
    return ("TODO", "AI Controls")


@pytest.fixture()
def prefs_list():
    """Provide an empty prefs list for the driver fixture."""
    return []


@pytest.fixture()
def about_prefs(driver: Firefox):
    """Fixture for AboutPrefs object navigated to AI Controls"""
    return AboutPrefs(driver)
