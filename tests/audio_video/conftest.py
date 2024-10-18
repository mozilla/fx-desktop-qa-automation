import pytest


@pytest.fixture()
def suite_id():
    return ("S1731", "Audio/Video")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
