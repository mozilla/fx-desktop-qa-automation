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

    # Close tabs below: right-click tab 3 and close all tabs after it (tabs 4 and 5)
    tabs.context_click(tabs.get_tab(3))
    context_menu.click_context_item("context-menu-close-multiple-tabs-to-right")
    tabs.wait_for_num_tabs(3)

    # Close tabs above: middle tab remains selected, close all tabs before it (tabs 1 and 2) via context menu
    context_menu.click_context_item("context-menu-close-multiple-tabs-to-left")
    tabs.wait_for_num_tabs(1)

    # Open 3 more tabs
    driver.switch_to.window(driver.window_handles[0])
    tabs.open_urls_in_tabs(["about:robots", "about:logo", "about:mozilla"])
    tabs.wait_for_num_tabs(4)

    # One tab is selected, close other tabs
    context_menu.click_on("context-menu-close-multiple-tabs-other-tabs")
    tabs.wait_for_num_tabs(1)
