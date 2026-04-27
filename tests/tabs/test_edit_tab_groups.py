import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar

NUM_TABS = 2
INITIAL_NAME = "group1"
NEW_NAME = "group2"
NEW_COLOR = "purple"


@pytest.fixture()
def test_case():
    return "2793048"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.tabs.groups.enabled", True),
        ("browser.tabs.groups.dragOverThresholdPercent", 20),
    ]


def test_edit_tab_group_panel(driver: Firefox):
    """
    C2793048 - Click the Tab Group name, edit the name, change the color, add a new tab and verify the changes are applied
    """
    # Instantiate objects
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)

    # Create a tab group
    tabs.create_tab_group(NUM_TABS, INITIAL_NAME, context_menu)

    # Capture initial tab count and verify initial label
    initial_tab_count = len(driver.window_handles)
    assert tabs.get_tab_group_label() == INITIAL_NAME

    # Edit the tab group: change name, color, and add a new tab
    tabs.edit_tab_group(new_name=NEW_NAME, new_color=NEW_COLOR, add_new_tab=True)

    # Verify changes are applied
    assert len(driver.window_handles) == initial_tab_count + 1
    assert tabs.get_tab_group_label() == NEW_NAME
    assert tabs.get_tab_group_color() == NEW_COLOR
