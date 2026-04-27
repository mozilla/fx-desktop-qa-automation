import pytest

from modules.browser_object import TabBar
from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.page_object import AboutNetworking, AboutPrefs


@pytest.fixture()
def suite_id():
    return ("S6066", "Networking")


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
def prefs(driver):
    return AboutPrefs(driver, category="privacy")


@pytest.fixture()
def networking(driver):
    return AboutNetworking(driver)


@pytest.fixture()
def tabs(driver):
    return TabBar(driver)


@pytest.fixture()
def nav(driver):
    return Navigation(driver)


@pytest.fixture()
def panel_ui(driver):
    return PanelUi(driver)
