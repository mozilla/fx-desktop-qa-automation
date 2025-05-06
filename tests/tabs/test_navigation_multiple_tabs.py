import logging

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar


@pytest.fixture()
def test_case():
    return "134654"


def test_navigation_multiple_tabs(driver: Firefox):
    """C134647 - Verify that navigation through multiple tabs is allowed"""

    tabs = TabBar(driver)
    num_tabs = 20

    # Open multiple tabs
    for _ in range(num_tabs):
        tabs.new_tab_by_button()

    with driver.context(driver.CONTEXT_CHROME):
        # Get the last tab's initial position (x-axis)
        last_tab = tabs.get_tab(21)
        original_location_pre_left = last_tab.location["x"]

        # Scroll left via double click
        tabs.double_click("tab-scrollbox-left-button", labels=[])

        # Wait for left scroll to change position (x should increase)
        def tab_scrolled_left(d):
            current_pos = tabs.get_tab(21).location["x"]
            return current_pos > original_location_pre_left

        tabs.custom_wait(timeout=2).until(tab_scrolled_left)

        # Log and assert the position after left scroll
        new_location_post_left = tabs.get_tab(21).location["x"]
        logging.info(f"Left scroll - original x: {original_location_pre_left}")
        logging.info(f"Left scroll - new x: {new_location_post_left}")
        assert new_location_post_left > original_location_pre_left

        # Get the first tab's initial position (x-axis)
        first_tab = tabs.get_tab(1)
        original_location_pre_right = first_tab.location["x"]

        # Scroll right via double click
        tabs.double_click("tab-scrollbox-right-button", labels=[])

        # Wait for right scroll to change position (x should decrease)
        def tab_scrolled_right(d):
            current_pos = tabs.get_tab(1).location["x"]
            return current_pos < original_location_pre_right

        tabs.custom_wait(timeout=2).until(tab_scrolled_right)

        # Log and assert the position after right scroll
        new_location_post_right = tabs.get_tab(1).location["x"]
        logging.info(f"Right scroll - original x: {original_location_pre_right}")
        logging.info(f"Right scroll - new x: {new_location_post_right}")
        assert new_location_post_right < original_location_pre_right
