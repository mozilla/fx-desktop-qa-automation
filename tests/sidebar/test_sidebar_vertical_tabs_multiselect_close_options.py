import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, TabBar


@pytest.fixture()
def test_case():
    return "2652392"


def test_close_other_tabs(driver: Firefox, sys_platform: str):
    """
    C2652392 - Verify Close other tabs: multi-select tabs and close all unselected ones.
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)

    nav.toggle_vertical_tabs()
    tabs.open_urls_in_tabs(
        ["about:robots", "about:logo", "about:mozilla", "about:blank", "about:about"],
        open_first_in_current_tab=True,
    )
    tabs.wait_for_num_tabs(5)

    # Select tabs 2, 3, 4 via Ctrl/Cmd+click then close all others
    tabs.select_multiple_tabs_by_indices([2, 3, 4], sys_platform)
    tabs.context_click(tabs.get_tab(2))
    context_menu.click_context_item("context-menu-close-multiple-tabs")
    context_menu.click_and_hide_menu("context-menu-close-multiple-tabs-other-tabs")
    tabs.wait_for_num_tabs(3)


def test_close_tabs_above(driver: Firefox):
    """
    C2652392 - Verify Close tabs above: closes all tabs before the right-clicked tab.
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)

    nav.toggle_vertical_tabs()
    tabs.open_urls_in_tabs(
        ["about:robots", "about:logo", "about:mozilla", "about:blank"],
        open_first_in_current_tab=True,
    )
    tabs.wait_for_num_tabs(4)

    # Right-click tab 3 and close all tabs above it (tabs 1 and 2)
    tabs.context_click(tabs.get_tab(3))
    context_menu.click_context_item("context-menu-close-multiple-tabs")
    context_menu.click_and_hide_menu("context-menu-close-multiple-tabs-to-left")
    tabs.wait_for_num_tabs(2)


def test_close_tabs_below(driver: Firefox):
    """
    C2652392 - Verify Close tabs below: closes all tabs after the right-clicked tab.
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)

    nav.toggle_vertical_tabs()
    tabs.open_urls_in_tabs(
        ["about:robots", "about:logo", "about:mozilla", "about:blank"],
        open_first_in_current_tab=True,
    )
    tabs.wait_for_num_tabs(4)

    # Right-click tab 2 and close all tabs below it (tabs 3 and 4)
    tabs.context_click(tabs.get_tab(2))
    context_menu.click_context_item("context-menu-close-multiple-tabs")
    context_menu.click_and_hide_menu("context-menu-close-multiple-tabs-to-right")
    tabs.wait_for_num_tabs(2)
