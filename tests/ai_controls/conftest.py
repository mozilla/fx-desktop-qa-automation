import pytest

from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def suite_id():
    return ("71443", "AI Controls")


@pytest.fixture()
def prefs_list():
    """Provide an empty prefs list for the driver fixture."""
    return []


@pytest.fixture()
def about_prefs(driver):
    """Fixture for AboutPrefs object navigated to AI Controls"""
    return AboutPrefs(driver)
