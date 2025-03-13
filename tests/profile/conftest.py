import pytest
from selenium.webdriver import Firefox

from modules.page_object_about_pages import AboutProfiles


@pytest.fixture()
def suite_id():
    return ("S2119", "Startup and Profile")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = []
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def about_profiles(driver: Firefox):
    ap = AboutProfiles(driver)
    yield ap


@pytest.fixture()
def add_to_prefs_list():
    return []
