import pytest

from modules.browser_object import PanelUi, TabBar
from modules.browser_object_navigation import Navigation
from modules.components.dropdown import Dropdown
from modules.page_object import AboutNewtab, AboutPrefs, GenericPage


@pytest.fixture()
def suite_id():
    return ("2241", "Preferences")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = []
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []


@pytest.fixture()
def about_prefs_category():
    return "general"


@pytest.fixture()
def about_prefs(driver, about_prefs_category: str):
    return AboutPrefs(driver, category=about_prefs_category)


@pytest.fixture()
def tabs(driver):
    return TabBar(driver)


@pytest.fixture()
def about_new_tab(driver):
    return AboutNewtab(driver)


@pytest.fixture()
def drop_down_root(about_prefs: AboutPrefs):
    about_prefs.open()
    return about_prefs.get_element("home-new-tabs-dropdown")


@pytest.fixture()
def dropdown(driver, about_prefs, drop_down_root):
    return Dropdown(page=about_prefs, root=drop_down_root)


@pytest.fixture()
def panel_ui(driver):
    return PanelUi(driver)


@pytest.fixture()
def nav(driver):
    return Navigation(driver)


@pytest.fixture()
def test_url(driver):
    return driver.current_url


@pytest.fixture()
def generic_page(driver, test_url):
    return GenericPage(driver, url=test_url)
