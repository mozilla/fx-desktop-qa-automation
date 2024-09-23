import pytest


@pytest.fixture()
def suite_id():
    return ("S2525", "Bookmarks and History")


@pytest.fixture()
def add_prefs():
    return []


@pytest.fixture()
def set_prefs(add_prefs):
    """Set prefs"""
    prefs = [("browser.toolbars.bookmarks.visibility", "Always")]
    prefs.extend(add_prefs)
    return prefs
