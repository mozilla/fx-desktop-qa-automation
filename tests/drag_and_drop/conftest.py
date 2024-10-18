import pytest


@pytest.fixture()
def suite_id():
    return ("S5259", "Drag and Drop")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
