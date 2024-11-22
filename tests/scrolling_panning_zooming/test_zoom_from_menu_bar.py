import logging
import platform

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object_menu_bar import MenuBar
from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "165060"


TEST_PAGE = "https://www.example.com"


@pytest.mark.skipif(
    platform.system() == "Darwin", reason="Cannot access menubar in MacOS"
)
def test_zoom_from_menu_bar(driver: Firefox):
    """
    This test verifies that the X-coordinate of a <div> element's position
    changes appropriately when zooming in, resetting zoom, and zooming out
    using the Firefox menu bar controls. Additionally, it checks that the zoom
    level indicator updates correctly.
    """

    # Initialize the page and open the target URL
    page = GenericPage(driver, url=TEST_PAGE)
    page.open()
    nav = Navigation(driver)

    # Locate the main <div> element on the page
    div = driver.find_element(By.TAG_NAME, "div")
    initial_position = div.location["x"]  # Get the initial X position of the div
    logging.info(f"Initial X position of div: {initial_position}")

    # Access the Menu Bar
    menu_bar = MenuBar(driver)

    # **Step 1**: Open View > Zoom > Zoom In
    menu_bar.activate_menu_bar()
    menu_bar.open_menu("View")
    menu_bar.click_on("menu-bar-zoom")
    menu_bar.click_and_hide_menu("menu-bar-zoom-enlarge")

    # Wait for zoom to apply and get the new position of the <div>
    zoomed_in_position = driver.find_element(By.TAG_NAME, "div").location["x"]
    logging.info(f"X position of div after zoom-in: {zoomed_in_position}")

    # Switch to chrome context to check zoom level in the toolbar
    with driver.context(driver.CONTEXT_CHROME):
        zoom_button = nav.get_element("toolbar-zoom-level")
        zoom_level = zoom_button.get_attribute("label")
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

    # **Step 2**: Reset Zoom to 100%
    menu_bar.activate_menu_bar()
    menu_bar.open_menu("View")
    menu_bar.click_on("menu-bar-zoom")
    menu_bar.click_and_hide_menu("menu-bar-zoom-reset")

    # Wait for zoom reset to apply and get the reset position of the <div>
    reset_position = driver.find_element(By.TAG_NAME, "div").location["x"]
    logging.info(f"X position of div after zoom-reset: {reset_position}")

    # Check that the zoom button no longer exists
    with driver.context(driver.CONTEXT_CHROME):
        nav.element_not_visible("toolbar-zoom-level")

    # Assert that the X-coordinate after reset is back to the initial value
    assert (
        reset_position == initial_position
    ), f"Expected X position after zoom-reset to be {initial_position}, but got {reset_position}"

    # Assert that the X-coordinate after reset is back to the initial value
    assert (
        reset_position == initial_position
    ), f"Expected X position after zoom-reset to be {initial_position}, but got {reset_position}"

    # **Step 3**: Zoom Out
    menu_bar.open_menu("View")
    menu_bar.click_on("menu-bar-zoom")
    menu_bar.click_and_hide_menu("menu-bar-zoom-reduce")

    # Wait for zoom out to apply and get the new position of the <div>
    zoomed_out_position = driver.find_element(By.TAG_NAME, "div").location["x"]
    logging.info(f"X position of div after zoom-out: {zoomed_out_position}")

    # Switch to chrome context to check zoom level in the toolbar
    with driver.context(driver.CONTEXT_CHROME):
        zoom_button = nav.get_element("toolbar-zoom-level")
        zoom_level = zoom_button.get_attribute("label")
        logging.info(f"Zoom level after zoom-out: {zoom_level}")

        # Assert that the zoom level label is "90%" after zooming out
        assert (
            zoom_level == "90%"
        ), f"Expected zoom level to be '90%' after zoom-out, but got '{zoom_level}'"

    # Assert that the X-coordinate decreases after zooming out
    assert zoomed_out_position > reset_position, (
        f"Expected X position after zoom-out to be less than {reset_position}, "
        f"but got {zoomed_out_position}"
    )

    # Reset the zoom level back to 100%
    menu_bar.activate_menu_bar()
    menu_bar.open_menu("View")
    menu_bar.click_on("menu-bar-zoom")
    menu_bar.click_and_hide_menu("menu-bar-zoom-reset")
