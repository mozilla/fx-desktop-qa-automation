import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, Sidebar, TabBar


@pytest.fixture()
def test_case():
    return "2948255"


URLS = ["about:robots", "about:logo", "about:mozilla", "about:blank"]


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

    # Sidebar on the left
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    tabs.wait_for_num_tabs(4)

    # Multi-select tabs 2 and 3; pin and verify
    selected_tabs = tabs.select_multiple_tabs_by_indices([2, 3], sys_platform)
    tabs.context_click(selected_tabs[1])
    context_menu.click_and_hide_menu("context-menu-pin-selected-tabs")
    assert tabs.is_pinned(selected_tabs[0])
    assert tabs.is_pinned(selected_tabs[1])
    tabs.deselect_all_tabs()

    # Unpin and verify
    selected_tabs = tabs.select_multiple_tabs_by_indices([2, 3], sys_platform)
    tabs.context_click(selected_tabs[1])
    context_menu.click_and_hide_menu("context-menu-unpin-selected-tabs")
    assert not tabs.is_pinned(selected_tabs[0])
    assert not tabs.is_pinned(selected_tabs[1])
    tabs.deselect_all_tabs()

    # Move tabs 2 and 3 to end via multi-select
    selected_tabs = tabs.select_multiple_tabs_by_indices([2, 3], sys_platform)
    tabs.context_click(selected_tabs[0])
    context_menu.click_context_item("context-menu-move-tab")
    context_menu.click_and_hide_menu("context-menu-move-tab-to-end")
    tabs.wait_for_num_tabs(4)
    tabs.deselect_all_tabs()

    # Close tabs 2 and 3 via multi-select
    selected_tabs = tabs.select_multiple_tabs_by_indices([2, 3], sys_platform)
    tabs.context_click(selected_tabs[0])
    context_menu.click_on("context-menu-close-tab")
    tabs.wait_for_num_tabs(2)

    # Move Sidebar on the right
    driver.switch_to.window(driver.window_handles[0])
    sidebar.move_sidebar_to_right()

    # Open 4 fresh tabs for the right-side scenario
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=False)
    tabs.wait_for_num_tabs(6)

    # Multi-select tabs 5 and 6; pin and verify
    selected_tabs = tabs.select_multiple_tabs_by_indices([5, 6], sys_platform)
    tabs.context_click(selected_tabs[1])
    context_menu.click_and_hide_menu("context-menu-pin-selected-tabs")
    assert tabs.is_pinned(selected_tabs[0])
    assert tabs.is_pinned(selected_tabs[1])
    tabs.deselect_all_tabs()

    # Unpin and verify
    selected_tabs = tabs.select_multiple_tabs_by_indices([5, 6], sys_platform)
    tabs.context_click(selected_tabs[1])
    context_menu.click_and_hide_menu("context-menu-unpin-selected-tabs")
    assert not tabs.is_pinned(selected_tabs[0])
    assert not tabs.is_pinned(selected_tabs[1])
    tabs.deselect_all_tabs()

    # Move tabs 5 and 6 to end via multi-select
    selected_tabs = tabs.select_multiple_tabs_by_indices([5, 6], sys_platform)
    tabs.context_click(selected_tabs[0])
    context_menu.click_context_item("context-menu-move-tab")
    context_menu.click_and_hide_menu("context-menu-move-tab-to-end")
    tabs.wait_for_num_tabs(6)
    tabs.deselect_all_tabs()

    # Close tabs 5 and 6 via multi-select
    selected_tabs = tabs.select_multiple_tabs_by_indices([5, 6], sys_platform)
    tabs.context_click(selected_tabs[0])
    context_menu.click_on("context-menu-close-tab")
    tabs.wait_for_num_tabs(4)
