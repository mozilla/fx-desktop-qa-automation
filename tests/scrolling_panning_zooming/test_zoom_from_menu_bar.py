import logging
import platform
import pytest

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from modules.browser_object import PanelUi
from modules.browser_object_navigation import Navigation
from modules.browser_object_menu_bar import MenuBar
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "165060"


TEST_PAGE = "https://www.example.com"


def test_zoom_from_menu_bar(driver: Firefox):
    """
    This test verifies that the X-coordinate of a <div> element's position
    changes appropriately when zooming in using the Firefox menu bar controls.
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

    # Access the Menu Bar
    menu_bar = MenuBar(driver)

    # Skip for macOS if platform is Darwin
    if platform.system() != "Darwin":
        # Open View > Zoom > Zoom In
        menu_bar.open_menu("View")
        menu_bar.click_on("menu-bar-zoom")
        menu_bar.click_on("menu-bar-zoom-enlarge")

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
