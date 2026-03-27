import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, TabBar

NUM_TABS = 3
URLS = ["about:robots", "about:logo", "about:mozilla"]


@pytest.fixture()
def test_case():
    return "2652111"


def test_sidebar_vertical_tabs_move_options(driver: Firefox):
    """
    C2652111 - Verify that vertical tabs in the sidebar can be moved via context menu
    options (Start, End, New Window).
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)

    # Enable vertical tabs
    nav.toggle_vertical_tabs()

    # Open tabs
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    tabs.wait_for_num_tabs(NUM_TABS)

    # Record the middle tab handle and title before moving
    selected_handle = driver.window_handles[1]
    driver.switch_to.window(selected_handle)
    middle_tab_title = driver.title

    # Right-click the middle tab, open Move tab submenu, and verify options
    tabs.context_click(tabs.get_tab(2))
    context_menu.click_context_item("context-menu-move-tab")
    context_menu.element_visible("context-menu-move-tab-to-start")
    context_menu.element_visible("context-menu-move-tab-to-end")
    context_menu.element_visible("context-menu-move-to-new-window")
    tabs.hide_popup("tabContextMenu")

    # Move tab to Start and verify it is now the first tab
    tabs.context_click(tabs.get_tab(2))
    context_menu.click_and_hide_menu("context-menu-move-tab-to-start")
    tabs.hide_popup("tabContextMenu")
    driver.switch_to.window(driver.window_handles[0])
    assert driver.title == middle_tab_title

    # Move tab to End and verify it is now the last tab
    tabs.context_click(tabs.get_tab(2))
    context_menu.click_and_hide_menu("context-menu-move-tab-to-end")
    tabs.hide_popup("tabContextMenu")
    driver.switch_to.window(driver.window_handles[-1])
    assert driver.title == middle_tab_title

    # Move tab to New Window and verify the tab is in a new window
    tabs.context_click(tabs.get_tab(2))
    context_menu.click_and_hide_menu("context-menu-move-to-new-window")
    tabs.hide_popup("tabContextMenu")
    assert len(driver.window_handles) == NUM_TABS
    driver.switch_to.window(selected_handle)
    assert driver.title == middle_tab_title
