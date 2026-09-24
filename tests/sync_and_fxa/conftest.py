import pytest


@pytest.fixture()
def suite_id():
    return ("S2130", "Sync & Firefox Account")


@pytest.fixture()
def fxa_env():
    return "stage"


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = []
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []
