import pytest


@pytest.fixture()
def suite_id():
    return ("2085", "Find Toolbar")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
