import pytest


@pytest.fixture()
def suite_id():
    return ("5833", "Security and Privacy")


@pytest.fixture()
def add_prefs():
    return []


@pytest.fixture()
def set_prefs(add_prefs: dict):
    """Set prefs"""
    prefs = []
    prefs.extend(add_prefs)
    return prefs
