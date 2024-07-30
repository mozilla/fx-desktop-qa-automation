import pytest


@pytest.fixture()
def suite_id():
    return ("S67", "Crash Reporter")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
