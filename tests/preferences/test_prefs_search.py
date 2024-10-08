import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "N/A"


@pytest.mark.ci
def test_search_prefs(driver: Firefox):
    about_prefs = AboutPrefs(driver, category="general").open()
    about_prefs.find_in_settings("pri")
    about_prefs.element_visible("h2-enhanced-tracking-protection")
