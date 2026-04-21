import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar

NUM_TABS = 2
GROUP_NAME = "group1"


@pytest.fixture()
def test_case():
    return "2793046"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.tabs.groups.enabled", True),
        ("browser.tabs.groups.dragOverThresholdPercent", 20),
    ]


def test_group_tabs(driver: Firefox):
    """
    C2793046, verify adding Tab Groups from tab context menu.
    """

    tabs = TabBar(driver)
    tab_context_menu = ContextMenu(driver)

    # Create a tab group
    tabs.create_tab_group(NUM_TABS, GROUP_NAME, tab_context_menu)

    # Verify that the tab group is created
    tabs.element_exists("tabgroup-overflow-count")
    tabs.element_visible("tabgroup-line")
