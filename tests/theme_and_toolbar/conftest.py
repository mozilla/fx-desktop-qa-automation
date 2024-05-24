import pytest


@pytest.fixture()
def suite_id():
    return ("1997", "Theme and Toolbar")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
