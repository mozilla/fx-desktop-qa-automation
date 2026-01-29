import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar

NUM_TABS = 3
GROUP_NAME = "test_group"


@pytest.fixture()
def test_case():
    return "2793052"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.tabs.groups.enabled", True),
        ("browser.tabs.groups.dragOverThresholdPercent", 20),
    ]


def test_remove_tab_from_a_group(driver: Firefox):
    """
    C2793052 - Verify that a tab can be removed from a Tab Group via context menu.
    The removed tab should be displayed at the end of the group in the tab strip.
    """

    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)

    # Create a tab group with several tabs
    tabs.create_tab_group(NUM_TABS, GROUP_NAME, context_menu)
    tabs.add_tab_to_existing_group(3, context_menu)

    # Verify the group is created with multiple tabs
    tabs.verify_tab_group_visible()
    tabs.verify_tab_group_has_multiple_tabs()

    # Remove the first tab from the group
    tabs.remove_tab_from_group(1, context_menu)

    # Verify the tab group still exists with remaining tabs
    tabs.verify_tab_group_visible()
    tabs.verify_tab_group_has_multiple_tabs()

    # Verify the removed tab is displayed after the group in the tab strip
    tabs.verify_tab_after_group(1)
