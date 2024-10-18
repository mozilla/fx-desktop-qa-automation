import pytest


@pytest.fixture()
def suite_id():
    return ("S73", "Printing UI Modernization")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
