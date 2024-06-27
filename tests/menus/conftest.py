import pytest


@pytest.fixture()
def suite_id():
    return ("S85", "Menus")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
