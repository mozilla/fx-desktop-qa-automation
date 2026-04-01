import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, TabBar

NUM_TABS = 5
URLS = ["about:robots", "about:logo", "about:mozilla", "about:blank", "about:about"]


@pytest.fixture()
def test_case():
    return "2652384"


def test_sidebar_vertical_tabs_closing_options(driver: Firefox, sys_platform: str):
    """
    C2652384 - Verify that vertical tabs in the sidebar can be closed via context menu, keyboard shortcut (CTRL+W),
    the X button, and middle mouse click.
    """
    # Instantiate objects
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)

    # Enable vertical tabs and open tabs
    nav.toggle_vertical_tabs()
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    tabs.wait_for_num_tabs(NUM_TABS)

    # Close a tab via context menu
    tabs.context_click(tabs.get_tab(NUM_TABS))
    context_menu.click_and_hide_menu("context-menu-close-tab")
    tabs.wait_for_num_tabs(NUM_TABS - 1)

    # Close a tab via CTRL+W (CMD+W on Mac)
    driver.switch_to.window(driver.window_handles[-1])
    tabs.close_tab_shortcut(sys_platform)
    tabs.wait_for_num_tabs(NUM_TABS - 2)

    # Close a tab via the X (Close) button
    tab_to_close = tabs.get_tab(NUM_TABS - 2)
    tabs.close_tab(tab_to_close)
    tabs.wait_for_num_tabs(NUM_TABS - 3)

    # Close a tab via middle mouse click
    tabs.close_tab_by_middle_click(NUM_TABS - 3)
    tabs.wait_for_num_tabs(NUM_TABS - 4)
