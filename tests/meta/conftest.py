import pytest


@pytest.fixture()
def suite_id():
    return ("X", "No test case")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
