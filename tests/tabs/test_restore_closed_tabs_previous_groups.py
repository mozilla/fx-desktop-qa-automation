import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, PanelUi, TabBar

urls = [
    "https://example.com",
    "https://www.mozilla.org",
    "https://www.wikipedia.org",
    "https://www.python.org",
]

FIRST_GROUP = "Group 1"
SECOND_GROUP = "Group 2"


@pytest.fixture()
def test_case():
    return "2804875"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.tabs.groups.enabled", True),
        ("browser.tabs.groups.dragOverThresholdPercent", 20),
    ]


def test_restore_closed_tabs_previous_groups(driver: Firefox):
    """
    C2804875 - Verify that closed tabs can be restored to their previous Groups
    """

    # Instantiate objects
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    panel = PanelUi(driver)

    # Open 4 websites
    tabs.open_websites_in_tabs(urls)

    # Create Group 1 with tabs 1 and 2
    tabs.create_websites_tab_group(
        context_menu=context_menu,
        group_name=FIRST_GROUP,
        first_tab_index=1,
        additional_tab_indexes=[2],
    )

    # Create Group 2 with tabs 3 and 4
    tabs.create_websites_tab_group(
        context_menu=context_menu,
        group_name=SECOND_GROUP,
        first_tab_index=3,
        additional_tab_indexes=[4],
    )

    # Close a tab from the 2nd Group
    fourth_tab = tabs.get_tab(4)
    tabs.context_click(fourth_tab)
    context_menu.click_and_hide_menu("context-menu-close-tab")

    # Open the Recently closed tabs menu and restore the previously closed tab
    panel.reopen_all_recently_closed_tabs()

    # Check that the Tab is restore to the same Tab group as before in the same position
    # Wait for all tabs to be restored
    tabs.click_tab_by_title("Welcome to Python.org")
    assert tabs.get_active_tab_group_label() == SECOND_GROUP

    # Close a tab from each Tab group
    first_tab = tabs.get_tab(1)
    tabs.context_click(first_tab)
    context_menu.click_and_hide_menu("context-menu-close-tab")

    third_tab = tabs.get_tab(3)
    tabs.context_click(third_tab)
    context_menu.click_and_hide_menu("context-menu-close-tab")

    # Open the Recently closed tabs menu and restore all previously closed tabs
    panel.reopen_all_recently_closed_tabs()

    # Both tabs are restored to their respective Groups in the same position as before
    tabs.click_tab_by_title("Wikipedia")
    assert tabs.get_active_tab_group_label() == SECOND_GROUP

    tabs.click_tab_by_title("Example Domain")
    assert tabs.get_active_tab_group_label() == FIRST_GROUP
