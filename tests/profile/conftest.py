import pytest


@pytest.fixture()
def suite_id():
    return ("S2119", "Startup and Profile")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
