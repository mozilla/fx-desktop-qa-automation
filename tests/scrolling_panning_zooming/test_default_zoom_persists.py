import logging
import time

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import TabBar
from modules.page_object import AboutPrefs
from modules.page_object_generics import GenericPage

TEST_URL = "https://www.example.com"
DEFAULT_ZOOM_PERCENT = 150
TAB_COUNT = 3


@pytest.fixture()
def test_case():
    return "545730"


def _get_div_x_position(driver: Firefox) -> int:
    """
    Returns the X location of the first <div> element on the page.
    """
    div = driver.find_element(By.TAG_NAME, "div")
    return int(div.location["x"])


def _set_default_zoom(driver: Firefox, zoom_percent: int) -> None:
    """
    Sets the default zoom level in about:preferences.

    Args:
        zoom_percent: Zoom percentage (e.g., 150).
    """
    AboutPrefs(driver, category="general").open().set_default_zoom_level(zoom_percent)


def test_default_zoom_across_tabs(driver: Firefox):
    """
    Verify that the default zoom persists on different tabs by setting the zoom level
    to 150% and that the X-coordinate changes and is consistent across tabs.
    """

    # Step 1: Open the test page and record the initial position of the <div>
    page = GenericPage(driver, url=TEST_URL)
    page.open()

    initial_position = _get_div_x_position(driver)
    logging.info(f"Initial X position of div before setting zoom: {initial_position}")

    # Step 2: Open the browser preferences and set the default zoom level to 150%
    _set_default_zoom(driver, DEFAULT_ZOOM_PERCENT)

    # Step 3: Open three tabs, load the test URL, and verify the <div>'s position
    tabs = TabBar(driver)

    # Store the first tab's position after zoom change for consistency checks
    zoomed_position = None

    for index in range(1, TAB_COUNT + 1):
        # Open a new tab if not the first iteration
        if index > 0:
            tabs.new_tab_by_button()
            driver.switch_to.window(
                driver.window_handles[-1]
            )  # Switch to the newly opened tab

        # Load the test URL in the current tab
        page = GenericPage(driver, url=TEST_URL)
        page.open()

        current_position = _get_div_x_position(driver)
        logging.info(f"X position of div in tab {index + 1}: {current_position}")

        # Assert that the current position is different from the initial position
        assert current_position != initial_position, (
            f"Expected X position in tab {index + 1} to differ from the initial position "
            f"({initial_position}), but got {current_position}"
        )

        # Set the zoomed position for consistency checks if it's the first tab
        if zoomed_position is None:
            zoomed_position = current_position

        # Assert that the X-coordinate remains consistent across tabs
        assert current_position == zoomed_position, (
            f"Expected X position in tab {index + 1} to be {zoomed_position}, "
            f"but got {current_position}"
        )
