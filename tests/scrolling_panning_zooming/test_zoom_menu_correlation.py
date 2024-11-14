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
    This test verifies the position of a <div> element when zoom level changes using the Firefox menu controls.
    """

    # Initialize the page and open the target URL
    page = GenericPage(driver, url=TEST_PAGE)
    page.open()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # Locate the main <div> element on the page
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "div")))
    div = driver.find_element(By.TAG_NAME, "div")
    initial_position = div.location  # Get the initial position of the div
    logging.info(f"Initial position of div: {initial_position}")

    # Open the Firefox Menu panel
    panel = PanelUi(driver)
    panel.open_panel_menu()

    # **Step 1**: Zoom in using the "zoom-enlarge" control
    panel.click_on("zoom-enlarge")
    WebDriverWait(driver, 5)  # Wait for the zoom effect to take place
    zoomed_in_position = driver.find_element(By.TAG_NAME, "div").location
    logging.info(f"Position of div after zoom-in: {zoomed_in_position}")

    # Assert that the position has changed after zooming in
    assert zoomed_in_position != initial_position, (
        f"Expected the position of the div to change after zoom-in, "
        f"but it remained the same: {zoomed_in_position}"
    )

    # **Step 2**: Reset zoom to 100% using the "zoom-reset" control
    panel.click_on("zoom-reset")
    WebDriverWait(driver, 5)
    driver.execute_script("arguments[0].scrollIntoView();", div)
    reset_position = driver.find_element(By.TAG_NAME, "div").location
    logging.info(f"Position of div after zoom-reset: {reset_position}")

    # Assert that the position is back to the initial value
    assert reset_position == initial_position, (
        f"Expected the position of the div to return to initial position after zoom-reset, "
        f"but got: {reset_position}"
    )

    # **Step 3**: Zoom out using the "zoom-reduce" control
    panel.click_on("zoom-reduce")
    WebDriverWait(driver, 5)
    driver.execute_script("arguments[0].scrollIntoView();", div)
    zoomed_out_position = driver.find_element(By.TAG_NAME, "div").location
    logging.info(f"Position of div after zoom-out: {zoomed_out_position}")

    # Assert that the position has changed after zooming out
    assert zoomed_out_position != initial_position, (
        f"Expected the position of the div to change after zoom-out, "
        f"but it remained the same: {zoomed_out_position}"
    )
