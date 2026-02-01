import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar

# Local predictable URLs
URLS = [
    "about:about",
    "about:mozilla",
    "about:license",
]

# Move options
MOVE_TO_START = "context-menu-move-tab-to-start"
MOVE_TAB_MENU = "context-menu-move-tab"


@pytest.fixture()
def test_case():
    return "C1234567"


def test_move_tab_by_title_using_pom(driver: Firefox):
    """
    Test moving a tab to the start position using POM approach.
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)

    driver.get(URLS[0])
    tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(URLS[1])

    # We are now on the second tab (selected). Use selected-tab instead of get_tab(2)
    # to avoid index/linkedpanel mismatches that can make "Move to Start" disabled.
    title_to_move = driver.title

    tabs.context_click("selected-tab")
    context_menu.hover(MOVE_TAB_MENU)
    context_menu.element_visible(MOVE_TO_START)
    context_menu.click_on(MOVE_TO_START)

    # Hide the context menu
    tabs.hide_popup("tabContextMenu")

    # Verify the tab moved to start
    driver.switch_to.window(driver.window_handles[0])
    actual_title = driver.title

    assert title_to_move in actual_title, (
        f"Tab was not moved to start. Expected '{title_to_move}' at position 0, "
        f"but found '{actual_title}'"
    )
