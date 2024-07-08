import pytest


@pytest.fixture()
def suite_id():
    return ("S2241", "Preferences")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
