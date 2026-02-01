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


@pytest.mark.parametrize(
    "move_option",
    [
        MOVE_TO_START,
        MOVE_TO_END,
        MOVE_TO_NEW_WINDOW,
    ],
)
def test_move_single_tab(driver: Firefox, move_option: str):
    """
    Test moving a single tab via context menu.
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

    # For MOVE_TO_END, switch to first tab; otherwise stay on last tab
    if move_option == MOVE_TO_END:
        driver.switch_to.window(driver.window_handles[0])
        expected_title = first_title
    else:
        expected_title = third_title

    initial_window_count = len(driver.window_handles)

    # Right-click on the selected tab to open context menu
    tabs.context_click("selected-tab")

    # Hover over "Move Tab" to open submenu
    context_menu.hover(MOVE_TAB_MENU)

    # Wait for the submenu item to be visible and click it
    context_menu.element_visible(move_option)
    context_menu.click_on(move_option)

    time.sleep(5)

    # Verification based on move option
    if move_option == MOVE_TO_START:
        tabs.hide_popup("tabContextMenu")
        driver.switch_to.window(driver.window_handles[0])
        actual_title = driver.title

        assert expected_title in actual_title, (
            f"Tab was not moved to start. Expected '{expected_title}' at position 0, "
            f"but found '{actual_title}'"
        )

    elif move_option == MOVE_TO_END:
        tabs.hide_popup("tabContextMenu")
        driver.switch_to.window(driver.window_handles[-1])
        actual_title = driver.title

        assert expected_title in actual_title, (
            f"Tab was not moved to end. Expected '{expected_title}' at last position, "
            f"but found '{actual_title}'"
        )

    elif move_option == MOVE_TO_NEW_WINDOW:
        driver.switch_to.window(driver.window_handles[-1])
        new_window_count = len(driver.window_handles)
        new_window_title = driver.title

        assert new_window_count == initial_window_count, (
            f"Expected same number of handles (tab moved to new window), "
            f"but got {new_window_count} vs initial {initial_window_count}"
        )

        assert expected_title in new_window_title, (
            f"Tab was not moved to new window. Expected '{expected_title}' "
            f"but found '{new_window_title}'"
        )
