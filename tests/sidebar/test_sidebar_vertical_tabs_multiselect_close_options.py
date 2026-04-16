import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, TabBar

URLS = ["about:robots", "about:logo", "about:mozilla", "about:blank", "about:about"]


@pytest.fixture()
def test_case():
    return "2652392"


def test_sidebar_vertical_tabs_multiselect_close_options(
    driver: Firefox, sys_platform: str
):
    """
    C2652392 - Verify multi-select close options: close tabs above, close tabs below,
    and close other tabs.
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)

    nav.toggle_vertical_tabs()
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    tabs.wait_for_num_tabs(5)

    # Close other tabs: select tabs 2, 3, 4; close all unselected tabs (1 and 5)
    # In the multiselect vertical tabs context menu, close-other/above/below are top-level
    # items (not nested under a "Close Multiple Tabs" submenu), so no parent hover is needed.
    selected_tabs = tabs.select_multiple_tabs_by_indices([2, 3, 4], sys_platform)
    tabs.context_click(selected_tabs[0])
    context_menu.click_and_hide_menu("context-menu-close-multiple-tabs-other-tabs")
    tabs.hide_popup("tabContextMenu")
    tabs.wait_for_num_tabs(3)

    # Plain-click tab 3 to clear multiselection
    tabs.click_tab_by_index(3)

    # Close tabs above: right-click tab 3 (middle remaining) and close tab 2 above it
    tabs.context_click(tabs.get_tab(3))
    context_menu.click_context_item("context-menu-close-multiple-tabs-to-left")
    tabs.wait_for_num_tabs(2)

    # Close tabs below: right-click tab 3 (first of 2 remaining) and close tab 4 below it
    tabs.context_click(tabs.get_tab(3))
    context_menu.click_context_item("context-menu-close-multiple-tabs-to-right")
    tabs.wait_for_num_tabs(1)
