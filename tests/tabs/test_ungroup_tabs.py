import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar

NUM_TABS = 2
GROUP_NAME = ["group1", "group2", "group3"]


@pytest.fixture()
def test_case():
    return "2796550"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.tabs.groups.enabled", True),
        ("browser.tabs.groups.dragOverThresholdPercent", 20),
    ]


def test_ungroup_tabs(driver: Firefox):
    """
    C2796550, verify that grouped tab can be ungrouped.
             Since in the step2 a tab group still remains,
             it is executed after step3 to avoid tests
             dependency.
    """

    """
     Step 1
     Action:         Right click on one of the grouped Tabs and select Remove from Group.
     Verification:   The Selected Tab is removed from the group.
    """

    tabs = TabBar(driver)
    tab_context_menu = ContextMenu(driver)

    # Create a tab group
    tabs.create_tab_group(NUM_TABS, GROUP_NAME[0], tab_context_menu)

    # Remove first tab from the tab group
    first_tab = tabs.get_tab(1)
    tabs.context_click(first_tab)
    tab_context_menu.click_and_hide_menu("context-remove-tab-from-group")

    # Verify tab is removed from the tab group
    tabs.element_not_visible("tabgroup-overflow-count")

    """
     Step 3
     Action:         Right-click the created Tab Group and select Ungroup Tabs.
     Verification:   The Tab Group name and color is no longer displayed and all 
                     tabs are no longer part of any group.
    """

    # Create a tab group
    tabs.create_tab_group(NUM_TABS, GROUP_NAME[2], tab_context_menu)

    # Right-click on the group and select Ungroup Tabs.
    tabs.context_click("tabgroup-label")
    tabs.click_and_hide_menu("tabgroup-ungroup-tabs")

    # Verify tab group is no longer there
    tabs.element_not_visible("tabgroup-label")

    """
     Step 2
     Action:         Grab another tab and move it beyond a Tab that is outside the group.
     Verification:   The selected tab is no longer part of that Tab group.
    """

    # Create a tab group
    tabs.create_tab_group(NUM_TABS, GROUP_NAME[1], tab_context_menu)

    # Click the first tab, hold, move by offset, and then release
    first_tab = tabs.get_tab(1)
    tabs.set_chrome_context()
    tabs.actions.click_and_hold(first_tab).move_by_offset(120, 0).release().perform()

    # Verify tab is removed from the tab group
    tabs.element_not_visible("tabgroup-overflow-count")
