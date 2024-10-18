import pytest


@pytest.fixture()
def suite_id():
    return ("S102", "Scrolling, Panning and Zooming")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
