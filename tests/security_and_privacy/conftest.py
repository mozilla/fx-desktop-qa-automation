import pytest


@pytest.fixture()
def suite_id():
    return ("X", "Security and Privacy")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
