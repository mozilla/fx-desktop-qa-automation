import pytest
from selenium.common.exceptions import NoSuchElementException

from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def suite_id():
    return ("S71443", "AI Controls")


@pytest.fixture()
def prefs_list():
    return []


@pytest.fixture()
def about_prefs(driver):
    """Provide AboutPrefs configured for the AI category.
    Skips the entire test if the browser does not support about:preferences#ai
    (requires Firefox Nightly 152+).
    """
    ap = AboutPrefs(driver, category="ai")
    ap.open()
    try:
        ap.get_element("ai-controls-toggle")
    except (NoSuchElementException, Exception):
        pytest.skip("AI controls not available in this Firefox version")
    return ap
