import logging
import platform
import time

import pytest
from selenium.webdriver import ActionChains, Firefox, Keys
from selenium.webdriver.common.by import By

from modules.browser_object import ContextMenu, TabBar

# Title Constants
EXPECTED_MOZILLA_TITLE = "Mozilla"
EXPECTED_ROBOT_TITLE = "Gort!"
EXPECTED_WELCOME_TITLE = "Welcome"

MOVE_TO_END = "context-menu-move-tab-to-end"
MOVE_TO_START = "context-menu-move-tab-to-start"
MOVE_TO_NEW_WINDOW = "context-menu-move-to-new-window"


@pytest.fixture()
def test_case():
    return "246989"


@pytest.mark.parametrize(
    "move_option,expected_title,expected_position",
    [
        (MOVE_TO_END, EXPECTED_ROBOT_TITLE, 2),
        (MOVE_TO_START, EXPECTED_ROBOT_TITLE, 0),
        # (MOVE_TO_NEW_WINDOW, EXPECTED_ROBOT_TITLE, 0),
    ],
)
def test_move_multi_selected_tabs(
    driver: Firefox, sys_platform: str, move_option, expected_title, expected_position
):
    """Test all tab movement operations in separate test runs"""
    tab_movements(driver, sys_platform, move_option, expected_title, expected_position)


def tab_movements(
    driver: Firefox, sys_platform: str, move_option, expected_title, expected_position
):  # expected_position starts at index 0
    tabs = TabBar(driver)
    tab_context_menu = ContextMenu(driver)
    original_windows = None

    tab_titles = []
    url_list = ["https://mozilla.org", "about:robots", "about:welcome", "about:logo"]

    driver.get(url_list[0])
    tab_titles.append(driver.title)

    # Open 4 tabs
    for i in range(1, len(url_list)):
        tabs.new_tab_by_button()
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(url_list[i])
        tab_titles.append(driver.title)

    # Specific tabs we want to work with
    selected_tab_indices = [2, 3]
    selected_tabs = tabs.select_multiple_tabs_by_indices(
        selected_tab_indices, sys_platform
    )

    # move-to-- -repeated
    tabs.context_click(selected_tabs[1])
    tab_context_menu.click_and_hide_menu(move_option)
    tabs.hide_popup("tabContextMenu")

    # Verify for move-to-end/move-to-start
    driver.switch_to.window(driver.window_handles[expected_position])
    actual_title = driver.title
    assert expected_title in actual_title, (
        f"Expected '{expected_title}' at position {expected_position}"
    )
