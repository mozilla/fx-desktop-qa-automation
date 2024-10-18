import pytest


@pytest.fixture()
def suite_id():
    return ("S498", "Geolocation")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
