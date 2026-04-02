import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, TabBar

NUM_TABS = 5
URLS = ["about:robots", "about:logo", "about:mozilla", "about:blank", "about:about"]


@pytest.fixture()
def test_case():
    return "2652393"


def test_vertical_tabs_reopen_closed_tab(driver: Firefox):
    """
    C2652393 - Verify that a closed tab can be reopened in vertical tabs via context menu
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
    tab_to_close = tabs.get_tab(NUM_TABS)
    tabs.context_click(tab_to_close)
    context_menu.click_and_hide_menu("context-menu-close-tab")
    tabs.wait_for_num_tabs(NUM_TABS - 1)

    # Reopen the closed tab via context menu on another tab
    tabs.context_click(tabs.get_tab(NUM_TABS - 1))
    context_menu.click_and_hide_menu("context-menu-reopen-closed-tab")
    tabs.wait_for_num_tabs(NUM_TABS)

    # Verify the reopened tab is the correct one by checking its URL
    driver.switch_to.window(driver.window_handles[-1])
    nav.url_contains(URLS[-1])
