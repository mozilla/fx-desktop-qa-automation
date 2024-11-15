import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
import logging

from modules.browser_object import PanelUi
from modules.page_object_generics import GenericPage

@pytest.fixture()
def test_case():
    return "65064"

TEST_PAGE = "https://www.example.com"

def test_zoom_level_div_position(driver: Firefox):
    """
    This test verifies Verify that Zoom Indicator & Menu [≡]
    Zoom In [+] / Zoom Out [-] / Reset Zoom Level [%] are correctly displayed and functional
    """

    # Initialize the page and open the target URL
    page = GenericPage(driver, url=TEST_PAGE)
    page.open()

    # Locate the main <div> element on the page
    div = driver.find_element(By.TAG_NAME, "div")
    initial_position = div.location['x']  # Get the initial X position of the div
    logging.info(f"Initial X position of div: {initial_position}")

    # Assert the initial position X-coordinate is 238
    assert initial_position == 238, (
        f"Expected initial X position to be 238, but got {initial_position}"
    )

    # Open the Firefox Menu panel
    panel = PanelUi(driver)
    panel.open_panel_menu()

    # **Step 1**: Zoom in using the "zoom-enlarge" control
    panel.click_on("zoom-enlarge")
    zoomed_in_position = driver.find_element(By.TAG_NAME, "div").location['x']
    logging.info(f"X position of div after zoom-in: {zoomed_in_position}")

    # Assert the X-coordinate after zooming in is 298
    assert zoomed_in_position == 191, (
        f"Expected X position after zoom-in to be 298, but got {zoomed_in_position}"
    )

    # **Step 2**: Reset zoom to 100% using the "zoom-reset" control
    panel.click_on("zoom-reset")
    reset_position = driver.find_element(By.TAG_NAME, "div").location['x']
    logging.info(f"X position of div after zoom-reset: {reset_position}")

    # Assert the X-coordinate after reset is back to 238
    assert reset_position == 238, (
        f"Expected X position after zoom-reset to be 238, but got {reset_position}"
    )

    # **Step 3**: Zoom out using the "zoom-reduce" control
    panel.click_on("zoom-reduce")
    zoomed_out_position = driver.find_element(By.TAG_NAME, "div").location['x']
    logging.info(f"X position of div after zoom-out: {zoomed_out_position}")

    # Assert the X-coordinate after zooming out is 191
    assert zoomed_out_position == 298, (
        f"Expected X position after zoom-out to be 191, but got {zoomed_out_position}"
    )
