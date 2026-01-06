import pytest

from modules.browser_object import PrintPreview


@pytest.fixture()
def suite_id():
    return ("S73", "Printing UI Modernization")


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
def print_preview(driver):
    return PrintPreview(driver)
