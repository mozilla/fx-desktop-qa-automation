import pytest


@pytest.fixture()
def suite_id():
    return ("S2525", "Bookmarks and History")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
