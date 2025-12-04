import pytest
from selenium.webdriver import Firefox
from modules.browser_object import TabBar, ContextMenu
from selenium.webdriver.common.action_chains import ActionChains


NUM_TABS = 2
GROUP_NAME1 = "group1"
GROUP_NAME2 = "group2"
GROUP_NAME3 = "group3"

@pytest.fixture()
def test_case():
    return "2796550"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.tabs.groups.enabled", True),
            ("browser.tabs.groups.dragOverThresholdPercent", 20)]


@pytest.fixture()
def create_tab_group(driver: Firefox):
    """Create a new tab group"""

    tabs = TabBar(driver)
    tab_context_menu = ContextMenu(driver)

    # Open few tabs
    for i in range(NUM_TABS):
        tabs.new_tab_by_button()

    tabs.wait_for_num_tabs(NUM_TABS+1)

    # Add the first tab into a New Group
    first_tab = tabs.get_tab(1)
    tabs.context_click(first_tab)
    tab_context_menu.click_and_hide_menu("context-move-tab-to-new-group")

    # Wait for tab group menu to open
    tabs.element_visible("tabgroup-input")

    # Enter a group Name and create group
    tabs.fill("tabgroup-input",GROUP_NAME1, clear_first=False)

    # Make sure the group is created
    tabs.element_visible("tabgroup-label")

    # Add the second tab into existing Group
    second_tab = tabs.get_tab(2)
    tabs.context_click(second_tab)
    tab_context_menu.click_on("context-move-tab-to-group")
    tabs.click_and_hide_menu("tabgroup-menuitem")

    # Verify that tabs are grouped
    tabs.element_exists("tabgroup-overflow-count")
    tabs.element_visible("tabgroup-line")

    # Switch to chrome context
    tabs.set_chrome_context()

    # Verify the count
    tabs.expect_element_attribute_contains("tabgroup-overflow-count", "aria-description", "1 more tab")

    return tabs, tab_context_menu


def test_ungrouping_tab_1(create_tab_group):
    """
    C2796550, verify that grouped tab can be ungrouped.

    Action:         Right click on one of the grouped Tabs and select Remove from Group.
    Verification:   The Selected Tab is removed from the group.

    """

    tabs, tab_context_menu = create_tab_group

    # Remove first tab from the tab group
    first_tab = tabs.get_tab(1)
    tabs.context_click(first_tab)
    tab_context_menu.click_and_hide_menu("context-remove-tab-from-group")

    # Verify tab is removed from the tab group
    tabs.element_not_visible("tabgroup-overflow-count")


def test_ungrouping_tab_2(create_tab_group, driver: Firefox):
    """
    C2796550, verify that grouped tab can be ungrouped.

    Action:         Grab another tab and move it beyond a Tab that is outside the group.
    Verification:   The selected tab is no longer part of that Tab group.

    """

    tabs, tab_context_menu = create_tab_group

    # Create an ActionChains object
    actions = ActionChains(driver)

    # Click the first tab, hold, move by offset, and then release
    first_tab = tabs.get_tab(1)
    actions.click_and_hold(first_tab) \
           .move_by_offset(120, 0) \
           .release() \
           .perform()

    # Verify tab is removed from the tab group
    tabs.element_not_visible("tabgroup-overflow-count")


def test_ungrouping_tab_3(create_tab_group):
    """
    C2796550, verify that grouped tab can be ungrouped.

    Action:         Right-Click the created Tab Group and select Ungroup Tabs.
    Verification:   The Tab Group name and color is no longer displayed and all tabs are no longer a part of any group

    """

    tabs, tab_context_menu = create_tab_group

    # Right-click on the group and select Ungroup Tabs.
    tabs.context_click("tabgroup-label")
    tabs.click_on("tabgroup-ungroup-tabs")

    # Verify tab group is no longer there
    tabs.element_not_visible("tabgroup-label")