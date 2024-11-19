import logging
import platform
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


TEST_PAGE = "https://www.example.com"


# Skip this test if running on macOS
@pytest.mark.skipif(
    platform.system() == "Darwin",
    reason="Test skipped on macOS due to incompatible zoom controls",
)
def test_mouse_wheel_zoom(driver: Firefox):
    """
    This test verifies that the X-coordinate of a <div> element's position
    changes appropriately when zooming in and out mouse wheel menu controls.
    Additionally, it checks that the zoom level indicator updates correctly.
    """

    # Initialize the page and open the target URL
    page = GenericPage(driver, url=TEST_PAGE)
    page.open()
    nav = Navigation(driver)

    # Locate the main <div> element on the page
    div = driver.find_element(By.TAG_NAME, "div")
    initial_position = div.location["x"]  # Get the initial X position of the div
    logging.info(f"Initial X position of div: {initial_position}")

    # Initialize ActionChains for zooming with Ctrl + Mouse Wheel
    actions = ActionChains(driver)

    # **Step 1**: Zoom in using Ctrl + Mouse Wheel Scroll Up
    actions.key_down(Keys.CONTROL).scroll_by_amount(0, -100).key_up(
        Keys.CONTROL
    ).perform()
    time.sleep(1)  # Allow time for the zoom effect to take place
    zoomed_in_position = driver.find_element(By.TAG_NAME, "div").location["x"]
    logging.info(f"X position of div after zoom-in: {zoomed_in_position}")

    # Switch to chrome context to check zoom level in the toolbar
    with driver.context(driver.CONTEXT_CHROME):
        zoom_button = nav.get_element("toolbar-zoom-level")
        zoom_level = nav.get_element("toolbar-zoom-level").get_attribute("label")
        logging.info(f"Zoom level after zoom-in: {zoom_level}")

        # Assert that the zoom level label is "110%" after zooming in
        assert (
            zoom_level == "110%"
        ), f"Expected zoom level to be '110%' after zoom-in, but got '{zoom_level}'"

    # Assert that the X-coordinate increases after zooming in
    assert zoomed_in_position < initial_position, (
        f"Expected X position after zoom-in to be greater than {initial_position}, "
        f"but got {zoomed_in_position}"
    )

    # **Step 2**: Reset zoom to 100% using the keyboard shortcut (Ctrl + 0)
    with driver.context(driver.CONTEXT_CHROME):
        actions.key_down(Keys.CONTROL).send_keys("0").key_up(Keys.CONTROL).perform()
    time.sleep(1)  # Allow time for reset effect to take place
    reset_position = driver.find_element(By.TAG_NAME, "div").location["x"]
    logging.info(f"X position of div after zoom-reset: {reset_position}")

    # Check that the zoom button no longer exists
    with driver.context(driver.CONTEXT_CHROME):
        nav.element_not_visible("toolbar-zoom-level")

    # Assert that the X-coordinate after reset is back to the initial value
    assert (
        reset_position == initial_position
    ), f"Expected X position after zoom-reset to be {initial_position}, but got {reset_position}"

    # **Step 3**: Zoom out using Ctrl + Mouse Wheel Scroll Down
    actions.key_down(Keys.CONTROL).scroll_by_amount(0, 100).key_up(
        Keys.CONTROL
    ).perform()
    time.sleep(1)  # Allow time for the zoom effect to take place
    zoomed_out_position = driver.find_element(By.TAG_NAME, "div").location["x"]
    logging.info(f"X position of div after zoom-out: {zoomed_out_position}")

    # Switch to chrome context to check zoom level in the toolbar
    with driver.context(driver.CONTEXT_CHROME):
        zoom_level = zoom_button.get_attribute("label")
        logging.info(f"Zoom level after zoom-out: {zoom_level}")

        # Assert that the zoom level label is "90%" after zooming out
        assert (
            zoom_level == "90%"
        ), f"Expected zoom level to be '90%' after zoom-out, but got '{zoom_level}'"

    # Assert that the X-coordinate decreases after zooming out
    assert zoomed_out_position > initial_position, (
        f"Expected X position after zoom-out to be less than {initial_position}, "
        f"but got {zoomed_out_position}"
    )
