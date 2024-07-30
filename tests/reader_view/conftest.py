import pytest


@pytest.fixture()
def suite_id():
    return ("S2126", "Reader View")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
