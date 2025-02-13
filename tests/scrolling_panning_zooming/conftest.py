import pytest


@pytest.fixture()
def suite_id():
    return ("S102", "Scrolling, Panning and Zooming")


@pytest.fixture()
def add_prefs():
    return []


@pytest.fixture()
def set_prefs(add_prefs: dict):
    """Set prefs"""
    prefs = [
        ("browser.aboutConfig.showWarning", False),
    ]
    prefs.extend(add_prefs)
    return prefs
