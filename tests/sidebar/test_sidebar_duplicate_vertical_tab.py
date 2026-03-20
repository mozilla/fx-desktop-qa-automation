import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, Sidebar, TabBar

URL = "about:robots"


@pytest.fixture()
def test_case():
    return "2652112"


def test_sidebar_duplicate_vertical_tab(driver: Firefox):
    """
    C2652112 - Verify that duplicate tabs can be closed from the context menu when vertical tabs are displayed in the
    sidebar.
    """
    # Instantiate objects
    tabs = TabBar(driver)
    sidebar = Sidebar(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)

    # Enable vertical tabs via toolbar context menu
    nav.enable_vertical_tabs()

    # Open the same URL in two tabs to create duplicates
    tabs.open_urls_in_tabs([URL, URL], open_first_in_current_tab=True)
    tabs.wait_for_num_tabs(2)

    # Select a duplicate tab and right click to reveal options
    duplicate_tab = tabs.get_tab(2)
    tabs.context_click(duplicate_tab)

    # Verify "Close duplicate tabs" option is displayed in the context menu
    assert context_menu.element_visible("context-close-duplicate-tabs")

    # Click "Close duplicate tabs" and verify the duplicate tab is closed
    context_menu.click_and_hide_menu("context-close-duplicate-tabs")
    tabs.wait_for_num_tabs(1)

    # Verify "Closed 1 tab" confirmation message is displayed
    assert sidebar.element_visible("confirmation-hint")
