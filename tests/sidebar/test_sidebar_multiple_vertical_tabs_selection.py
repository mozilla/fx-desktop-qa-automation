import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, Sidebar, TabBar


@pytest.fixture()
def test_case():
    return "2948255"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("sidebar.revamp", True),
        ("sidebar.expandOnHover", True),
    ]


def test_sidebar_multiple_vertical_tabs_selection(driver: Firefox, sys_platform: str):
    """
    C2948255 - Verify that multiple vertical tabs can be moved, closed, pinned, and unpinned
    via the context menu with the sidebar positioned on the left and on the right.
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)
    sidebar = Sidebar(driver)

    nav.toggle_vertical_tabs()

    # === Sidebar on the left ===
    tabs.open_urls_in_tabs(
        ["about:robots", "about:logo", "about:mozilla", "about:blank"],
        open_first_in_current_tab=True,
    )
    tabs.wait_for_num_tabs(4)

    # Multi-select tabs 2 and 3; pin and verify
    selected_tabs = tabs.select_multiple_tabs_by_indices([2, 3], sys_platform)
    tabs.context_click(selected_tabs[1])
    context_menu.click_and_hide_menu("context-menu-pin-selected-tabs")
    assert tabs.is_pinned(selected_tabs[0])
    assert tabs.is_pinned(selected_tabs[1])

    # Unpin and verify
    selected_tabs = tabs.select_multiple_tabs_by_indices([2, 3], sys_platform)
    tabs.context_click(selected_tabs[1])
    context_menu.click_and_hide_menu("context-menu-unpin-selected-tabs")
    assert not tabs.is_pinned(selected_tabs[0])
    assert not tabs.is_pinned(selected_tabs[1])

    # Move tabs 2 and 3 to start via multi-select
    selected_tabs = tabs.select_multiple_tabs_by_indices([2, 3], sys_platform)
    tabs.context_click(selected_tabs[0])
    context_menu.click_context_item("context-menu-move-tab")
    context_menu.click_and_hide_menu("context-menu-move-tab-to-start")
    tabs.wait_for_num_tabs(4)

    # Close tabs 3 and 4 via multi-select
    selected_tabs = tabs.select_multiple_tabs_by_indices([3, 4], sys_platform)
    tabs.context_click(selected_tabs[0])
    context_menu.click_and_hide_menu("context-menu-close-tab")
    tabs.wait_for_num_tabs(3)

    # === Sidebar on the right ===
    driver.switch_to.window(driver.window_handles[0])
    sidebar.move_sidebar_to_right()

    # Open 4 fresh tabs (indices 5, 6, 7, 8) for the right-side scenario
    tabs.open_urls_in_tabs(
        ["about:robots", "about:logo", "about:mozilla", "about:blank"],
        open_first_in_current_tab=False,
    )
    # tabs.wait_for_num_tabs(6)  # tabs 1, 2, 5, 6, 7, 8

    # Multi-select tabs 5 and 6; pin and verify
    selected_tabs = tabs.select_multiple_tabs_by_indices([5, 6], sys_platform)
    tabs.context_click(selected_tabs[1])
    context_menu.click_and_hide_menu("context-menu-pin-selected-tabs")
    assert tabs.is_pinned(selected_tabs[0])
    assert tabs.is_pinned(selected_tabs[1])

    # Unpin and verify
    selected_tabs = tabs.select_multiple_tabs_by_indices([5, 6], sys_platform)
    tabs.context_click(selected_tabs[1])
    context_menu.click_and_hide_menu("context-menu-unpin-selected-tabs")
    assert not tabs.is_pinned(selected_tabs[0])
    assert not tabs.is_pinned(selected_tabs[1])

    # Move tabs 5 and 6 to start via multi-select
    selected_tabs = tabs.select_multiple_tabs_by_indices([5, 6], sys_platform)
    tabs.context_click(selected_tabs[0])
    context_menu.click_context_item("context-menu-move-tab")
    context_menu.click_and_hide_menu("context-menu-move-tab-to-start")
    tabs.wait_for_num_tabs(7)

    # Close tabs 7 and 8 via multi-select
    selected_tabs = tabs.select_multiple_tabs_by_indices([7, 8], sys_platform)
    tabs.context_click(selected_tabs[0])
    context_menu.click_and_hide_menu("context-menu-close-tab")
    tabs.wait_for_num_tabs(6)
