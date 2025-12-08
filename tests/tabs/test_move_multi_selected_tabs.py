import time

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar

# Title Constants
EXPECTED_ROBOT_TITLE = "Gort!"
EXPECTED_WELCOME_TITLE = "Welcome"

# Move options
MOVE_TO_END = "context-menu-move-tab-to-end"
MOVE_TO_START = "context-menu-move-tab-to-start"
MOVE_TO_NEW_WINDOW = "context-menu-move-to-new-window"

# Tab Positions (4 tabs in total)
FIRST_TAB_POSITION = 0
SECOND_TAB_POSITION = 1
THIRD_TAB_POSITION = 2
LAST_TAB_POSITION = 3


@pytest.fixture()
def test_case():
    return "246989"


@pytest.mark.parametrize(
    "move_option,expected_titles,expected_positions",
    [
        (
            MOVE_TO_END,
            (EXPECTED_ROBOT_TITLE, EXPECTED_WELCOME_TITLE),
            (THIRD_TAB_POSITION, LAST_TAB_POSITION),
        ),
        (
            MOVE_TO_START,
            (EXPECTED_ROBOT_TITLE, EXPECTED_WELCOME_TITLE),
            (FIRST_TAB_POSITION, SECOND_TAB_POSITION),
        ),
        (
            MOVE_TO_NEW_WINDOW,
            (None),
            (None),
        ),
    ],
)
def test_move_multi_selected_tabs(
    driver: Firefox, sys_platform: str, move_option, expected_titles, expected_positions
):
    """Test all tab movement operations in separate test runs"""
    tab_movements(
        driver, sys_platform, move_option, expected_titles, expected_positions
    )


def tab_movements(
    driver: Firefox, sys_platform: str, move_option, expected_titles, expected_positions
):
    tabs = TabBar(driver)
    tab_context_menu = ContextMenu(driver)
    original_windows = None

    tab_titles = []
    url_list = ["about:logo", "about:robots", "about:welcome", "https://mozilla.org"]

    # Open 4 tabs
    driver.get(url_list[0])
    tab_titles.append(driver.title)

    for i in range(1, len(url_list)):
        tabs.new_tab_by_button()
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(url_list[i])
        tab_titles.append(driver.title)

    # Specific tabs we want to move
    selected_tab_indices = [2, 3]  # Here indices start from 1
    selected_tabs = tabs.select_multiple_tabs_by_indices(
        selected_tab_indices, sys_platform
    )

    if move_option == MOVE_TO_NEW_WINDOW:
        windows_pos = set()
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            rect = driver.get_window_rect()
            windows_pos.add((rect["width"], rect["height"]))

        tabs.context_click(selected_tabs[1])
        tab_context_menu.click_and_hide_menu(move_option)
        tabs.hide_popup("tabContextMenu")

        time.sleep(2)

        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            rect = driver.get_window_rect()
            windows_pos.add((rect["width"], rect["height"]))

        assert len(windows_pos) > 1

    elif move_option in (MOVE_TO_END, MOVE_TO_START):
        assert expected_positions is not None
        assert expected_titles is not None

        # move-to-___
        tabs.context_click(selected_tabs[1])
        tab_context_menu.click_and_hide_menu(move_option)
        tabs.hide_popup("tabContextMenu")

        # Verify for move-to-end/move-to-start

        for expected_title, expected_position in zip(
            expected_titles, expected_positions
        ):
            # Switch to the window handle at the expected index
            # NOTE: driver.window_handles are the HANDLES, the index is the order they APPEAR
            driver.switch_to.window(driver.window_handles[expected_position])

            actual_title = driver.title

            # Assert the title is correct
            assert expected_title in actual_title, (
                f"Verification failed for tab at index {expected_position}: "
                f"Expected title '{expected_title}' but found '{actual_title}'."
            )
