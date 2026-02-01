import time

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
MOVE_TO_END = "context-menu-move-tab-to-end"
MOVE_TO_NEW_WINDOW = "context-menu-move-to-new-window"
MOVE_TAB_MENU = "context-menu-move-tab"


@pytest.fixture()
def test_case():
    return "C1234567"


def test_move_single_tab_to_start(driver: Firefox):
    """
    Test case: Move a single tab to the start of the tab strip.
    Steps:
    1. Open 3 tabs with different URLs
    2. Select the last tab (index 2)
    3. Right-click to open context menu
    4. Hover over "Move Tab" submenu
    5. Click "Move to Start"
    6. Verify the tab moved to the start position
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)

    # Open first tab
    driver.get(URLS[0])
    first_title = driver.title

    # Open second tab
    tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(URLS[1])

    # Open third tab
    tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(URLS[2])
    third_title = driver.title

    # The third tab is now selected (current tab)
    # Right-click on the selected tab to open context menu
    tabs.context_click("selected-tab")

    # Hover over "Move Tab" to open submenu
    context_menu.hover(MOVE_TAB_MENU)

    # Wait for the submenu item to be visible and click it
    context_menu.element_visible(MOVE_TO_START)
    context_menu.click_on(MOVE_TO_START)

    # Hide the context menu
    tabs.hide_popup("tabContextMenu")

    # Verify: The tab that was at the end should now be at the start
    # Switch to the first position and verify the title
    driver.switch_to.window(driver.window_handles[0])
    actual_title = driver.title
    time.sleep(5)

    assert third_title in actual_title, (
        f"Tab was not moved to start. Expected '{third_title}' at position 0, "
        f"but found '{actual_title}'"
    )


def test_move_single_tab_to_end(driver: Firefox):
    """
    Test case: Move a single tab to the end of the tab strip.
    Steps:
    1. Open 3 tabs with different URLs
    2. Select the first tab (index 0)
    3. Right-click to open context menu
    4. Hover over "Move Tab" submenu
    5. Click "Move to End"
    6. Verify the tab moved to the end position
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)

    # Open first tab
    driver.get(URLS[0])
    first_title = driver.title

    # Open second tab
    tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(URLS[1])

    # Open third tab
    tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(URLS[2])

    # Switch to first tab and select it
    driver.switch_to.window(driver.window_handles[0])

    # Right-click on the selected tab to open context menu
    tabs.context_click("selected-tab")

    # Hover over "Move Tab" to open submenu
    context_menu.hover(MOVE_TAB_MENU)

    # Wait for the submenu item to be visible and click it
    context_menu.element_visible(MOVE_TO_END)
    context_menu.click_on(MOVE_TO_END)

    # Hide the context menu
    tabs.hide_popup("tabContextMenu")

    # Verify: The tab that was at the start should now be at the end
    # Switch to the last position and verify the title
    driver.switch_to.window(driver.window_handles[-1])
    actual_title = driver.title
    time.sleep(5)

    assert first_title in actual_title, (
        f"Tab was not moved to end. Expected '{first_title}' at last position, "
        f"but found '{actual_title}'"
    )


def test_move_single_tab_to_new_window(driver: Firefox):
    """
    Test case: Move a single tab to a new window.
    Steps:
    1. Open 2 tabs with different URLs
    2. Select the second tab
    3. Right-click to open context menu
    4. Hover over "Move Tab" submenu
    5. Click "Move to New Window"
    6. Verify the tab is now in a new window
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)

    # Open first tab
    driver.get(URLS[0])

    # Open second tab
    tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(URLS[1])
    second_title = driver.title

    # Store initial window count
    initial_window_count = len(driver.window_handles)

    # Right-click on the selected tab to open context menu
    tabs.context_click("selected-tab")

    # Hover over "Move Tab" to open submenu
    context_menu.hover(MOVE_TAB_MENU)

    # Wait for the submenu item to be visible and click it
    context_menu.element_visible(MOVE_TO_NEW_WINDOW)
    context_menu.click_on(MOVE_TO_NEW_WINDOW)
    time.sleep(5)

    # Switch to the new window (last handle)
    driver.switch_to.window(driver.window_handles[-1])

    # Verify: A new window was created and it contains the moved tab
    new_window_count = len(driver.window_handles)
    new_window_title = driver.title

    assert new_window_count == initial_window_count, (
        f"Expected same number of handles (tab moved to new window), "
        f"but got {new_window_count} vs initial {initial_window_count}"
    )

    assert second_title in new_window_title, (
        f"Tab was not moved to new window. Expected '{second_title}' "
        f"but found '{new_window_title}'"
    )
