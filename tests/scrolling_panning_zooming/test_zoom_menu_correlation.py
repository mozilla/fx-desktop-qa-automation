import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

from modules.browser_object import PanelUi
from modules.page_object_generics import GenericPage

@pytest.fixture()
def test_case():
    return "65064"

TEST_PAGE = "https://www.example.com"

def test_zoom_level_div_position(driver: Firefox):
    """
    This test verifies that the X-coordinate of a <div> element's position
    changes appropriately when zooming in and out using the Firefox menu controls.
    """

    # Initialize the page and open the target URL
    page = GenericPage(driver, url=TEST_PAGE)
    page.open()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # Locate the main <div> element on the page
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "div")))
    div = driver.find_element(By.TAG_NAME, "div")
    initial_position = div.location['x']  # Get the initial X position of the div
    logging.info(f"Initial X position of div: {initial_position}")

    # Open the Firefox Menu panel
    panel = PanelUi(driver)
    panel.open_panel_menu()

    # **Step 1**: Zoom in using the "zoom-enlarge" control
    panel.click_on("zoom-enlarge")
    zoomed_in_position = driver.find_element(By.TAG_NAME, "div").location['x']
    logging.info(f"X position of div after zoom-in: {zoomed_in_position}")

    # Assert that the X-coordinate increases after zooming in
    assert zoomed_in_position < initial_position, (
        f"Expected X position after zoom-in to be greater than {initial_position}, "
        f"but got {zoomed_in_position}"
    )

    # **Step 2**: Reset zoom to 100% using the "zoom-reset" control
    panel.click_on("zoom-reset")
    reset_position = driver.find_element(By.TAG_NAME, "div").location['x']
    logging.info(f"X position of div after zoom-reset: {reset_position}")

    # Assert that the X-coordinate after reset is back to the initial value
    assert reset_position == initial_position, (
        f"Expected X position after zoom-reset to be {initial_position}, but got {reset_position}"
    )

    # **Step 3**: Zoom out using the "zoom-reduce" control
    panel.click_on("zoom-reduce")
    zoomed_out_position = driver.find_element(By.TAG_NAME, "div").location['x']
    logging.info(f"X position of div after zoom-out: {zoomed_out_position}")

    # Assert that the X-coordinate decreases after zooming out
    assert zoomed_out_position > initial_position, (
        f"Expected X position after zoom-out to be less than {initial_position}, "
        f"but got {zoomed_out_position}"
    )
