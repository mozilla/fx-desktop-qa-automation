import pytest


@pytest.fixture()
def suite_id():
    return ("S102", "Scrolling, Panning and Zooming")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = [
        ("browser.aboutConfig.showWarning", False),
    ]
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []