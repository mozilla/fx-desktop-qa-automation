import pytest

from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def suite_id():
    return ("S71443", "AI Controls")


@pytest.fixture()
def prefs_list():
    return []


@pytest.fixture()
def about_prefs(driver):
    """Provide AboutPrefs configured for the AI category, already opened."""
    ap = AboutPrefs(driver, category="ai")
    ap.open()
    return ap
