import pytest

from modules.browser_object import TabBar


@pytest.fixture()
def suite_id():
    return ("68", "Session Restore")


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
def tabs(driver):
    return TabBar(driver)
