from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar


@pytest.fixture()
def test_case():
    return "2197845"


URLS = [
    "about:about",
    "about:mozilla",
    "about:logo",
    "about:robots",
]


def test_restore_multiple_closed_tabs(driver: Firefox, tabs: TabBar, sys_platform: str):
    """
    C2197845 - Verify that the keyboard shortcut restores multiple closed tabs.
    """
    context_menu = ContextMenu(driver)

    # Open 4 new tabs
    for i in range(4):
        tabs.new_tab_by_button()
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(URLS[i])
    tabs.wait_for_num_tabs(5)

    # Close those 4 tabs with tab context menu option
    original_tab = tabs.get_tab(1)
    tabs.context_click(original_tab)
    context_menu.click_context_item("context-menu-close-multiple-tabs")
    context_menu.click_and_hide_menu("context-menu-close-multiple-tabs-to-right")
    context_menu.hide_popup_by_child_node("context-menu-close-multiple-tabs")
    tabs.wait_for_num_tabs(1)

    # Use the method to restore the closed tabs with shortcut
    tabs.reopen_tabs_with_shortcut(sys_platform, count=1)
    tabs.wait_for_num_tabs(5)

    # Verify the tabs are restored
    open_urls = set()
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        open_urls.add(driver.current_url)

    for url in URLS:
        assert url in open_urls, f"Expected reopened tab with URL '{url}' not found"
