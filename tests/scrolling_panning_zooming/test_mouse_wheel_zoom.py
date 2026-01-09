import logging
import time

import pytest
from selenium.webdriver import ActionChains, Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "466431"


RESET_ZOOM_KEY = "0"

SCROLL_ZOOM_IN_Y = -100
SCROLL_ZOOM_OUT_Y = 100

EXPECTED_ZOOM_IN_LABEL = "110%"
EXPECTED_ZOOM_OUT_LABEL = "90%"

TEST_PAGE = "https://www.example.com"


def _get_div_x_position(driver: Firefox) -> int:
    """
    Returns the X location of the first <div> element on the page.
    """
    div = driver.find_element(By.TAG_NAME, "div")
    return int(div.location["x"])


def _zoom_with_ctrl_wheel(actions: ActionChains, scroll_y: int) -> None:
    """
    Zooms using Ctrl + mouse wheel (scroll).
    """
    actions.key_down(Keys.CONTROL).scroll_by_amount(0, scroll_y).key_up(
        Keys.CONTROL
    ).perform()


# This test is not compatible with MacOS wheel controls
def test_mouse_wheel_zoom(driver: Firefox):
    """
    This test verifies that the X-coordinate of a <div> element's position
    changes appropriately when zooming in and out mouse wheel menu controls.
    Additionally, it checks that the zoom level indicator updates correctly.
    """

    # Open the test page and record the initial position of the <div>
    page = GenericPage(driver, url=TEST_PAGE)
    page.open()

    initial_position = _get_div_x_position(driver)
    logging.info(f"Initial X position of div before setting zoom: {initial_position}")

    # **Step 1**: Zoom in using Ctrl + Mouse Wheel Scroll Up
    actions = ActionChains(driver)
    _zoom_with_ctrl_wheel(actions, SCROLL_ZOOM_IN_Y)

    zoomed_in_position = _get_div_x_position(driver)
    logging.info(f"X position of div after zoom-in: {zoomed_in_position}")

    # Check zoom level in the toolbar
    nav = Navigation(driver)

    nav.element_attribute_contains(
        name="toolbar-zoom-level",
        attr_name="label",
        attr_value=EXPECTED_ZOOM_IN_LABEL,
    )

    # Assert that the X-coordinate increases after zooming in
    assert zoomed_in_position < initial_position, (
        f"Expected X position after zoom-in to be greater than {initial_position}, "
        f"but got {zoomed_in_position}"
    )

    # **Step 2**: Reset zoom to 100% using the keyboard shortcut (Ctrl + 0)
    with driver.context(driver.CONTEXT_CHROME):
        actions.key_down(Keys.CONTROL).send_keys("0").key_up(Keys.CONTROL).perform()

    reset_position = _get_div_x_position(driver)
    logging.info(f"X position of div after zoom-reset: {reset_position}")

    # Check that the zoom button no longer exists
    with driver.context(driver.CONTEXT_CHROME):
        nav.element_not_visible("toolbar-zoom-level")

    # Assert that the X-coordinate after reset is back to the initial value
    assert reset_position == initial_position, (
        f"Expected X position after zoom-reset to be {initial_position}, but got {reset_position}"
    )

    # **Step 3**: Zoom out using Ctrl + Mouse Wheel Scroll Down
    actions.key_down(Keys.CONTROL).scroll_by_amount(0, SCROLL_ZOOM_OUT_Y).key_up(
        Keys.CONTROL
    ).perform()

    zoomed_out_position = _get_div_x_position(driver)
    logging.info(f"X position of div after zoom-out: {zoomed_out_position}")

    # Check zoom level in the toolbar
    nav.element_attribute_contains(
        name="toolbar-zoom-level",
        attr_name="label",
        attr_value=EXPECTED_ZOOM_OUT_LABEL,
    )

    # Assert that the X-coordinate decreases after zooming out
    assert zoomed_out_position > initial_position, (
        f"Expected X position after zoom-out to be less than {initial_position}, "
        f"but got {zoomed_out_position}"
    )

    # Reset the zoom level back to 100%
    with driver.context(driver.CONTEXT_CHROME):
        actions.key_down(Keys.CONTROL).send_keys(RESET_ZOOM_KEY).key_up(
            Keys.CONTROL
        ).perform()
