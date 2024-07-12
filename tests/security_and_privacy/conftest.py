import pytest


@pytest.fixture()
def suite_id():
    return ("X", "Security and Privacy")


@pytest.fixture()
def set_prefs(add_prefs=None):
    """Set prefs"""
    prefs = []
    if add_prefs is not None:
        prefs.extend(add_prefs)
    return prefs