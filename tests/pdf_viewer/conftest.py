import pytest


@pytest.fixture()
def suite_id():
    return ("S65", "PDF Viewer")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
