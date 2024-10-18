import pytest


@pytest.fixture()
def suite_id():
    return ("S6066", "Networking")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
