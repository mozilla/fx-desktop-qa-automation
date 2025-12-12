import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, TabBar

NUM_TABS = 2
GROUP_NAME = ["group1", "group2", "group3"]


@pytest.fixture()
def test_case():
    return "2793050"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.tabs.groups.enabled", True),
        ("browser.tabs.groups.dragOverThresholdPercent", 20),
    ]


@pytest.mark.parametrize(
    "enable_vertical_tabs, group_name",
    [
        (False, GROUP_NAME[0]),
        (True, GROUP_NAME[1]),
    ],
    ids=["default_tabs", "vertical_tabs"],
)
def test_save_and_close_tab_group(
    driver: Firefox, enable_vertical_tabs: bool, group_name: str
):
    """
    C2793050 - Verify that the user can Save and Close a tab group on two scenarios, with horizontal and vertical
    tabs enabled.
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)

    # Get initial number of tabs before creating the group
    initial_tab_count = len(driver.window_handles)

    # Enable vertical tabs when required for this parametrized case
    if enable_vertical_tabs:
        nav.context_click("toolbar-blank-space")
        context_menu.click_on("context-menu-vertical-tabs")

    # Create a tab group
    tabs.create_tab_group(NUM_TABS, group_name, context_menu)

    # Right-click the Tab Group label and select Save and Close Group
    tabs.save_and_close_tab_group()

    # After closing the group, we should be back to the initial number of tabs
    tabs.wait_for_num_tabs(initial_tab_count)

    # Verify the group label is removed
    tabs.element_not_visible("tabgroup-label")
