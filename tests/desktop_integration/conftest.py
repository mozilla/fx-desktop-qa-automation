import pytest


@pytest.fixture()
def suite_id():
    return "S1940", "Desktop Integrations"


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = [("browser.taskbarTabs.enabled", True)]
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []
