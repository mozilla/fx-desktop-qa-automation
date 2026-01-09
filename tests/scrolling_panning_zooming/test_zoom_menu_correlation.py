import logging

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import PanelUi
from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "165064"


def _get_div_x_position(driver: Firefox) -> int:
    """
    Returns the X location of the first <div> element on the page.
    """
    div = driver.find_element(By.TAG_NAME, "div")
    return int(div.location["x"])


EXPECTED_ZOOM_IN_LABEL = "110%"
EXPECTED_ZOOM_OUT_LABEL = "90%"

TEST_PAGE = "https://www.example.com"


def test_zoom_level_div_position(driver: Firefox):
    """
    This test verifies that the X-coordinate of a <div> element's position
    changes appropriately when zooming in and out using the Firefox menu controls.
    Additionally, it checks that the zoom level indicator updates correctly.
    """

    # Open the test page and record the initial position of the <div>
    page = GenericPage(driver, url=TEST_PAGE)
    page.open()

    # Locate the main <div> element on the page
    initial_position = _get_div_x_position(driver)
    logging.info(f"Initial X position of div: {initial_position}")

    # Open the Firefox Menu panel
    panel = PanelUi(driver)
    panel.open_panel_menu()

    # Zoom in using the "zoom-enlarge" control
    panel.click_on("zoom-enlarge")
    zoomed_in_position = _get_div_x_position(driver)
    logging.info(f"X position of div after zoom-in: {zoomed_in_position}")

    # Check zoom level in the toolbar
    nav = Navigation(driver)

    nav.element_attribute_contains(
        "toolbar-zoom-level",
        attr_name="label",
        attr_value=EXPECTED_ZOOM_IN_LABEL,
    )

    # Assert that the X-coordinate increases after zooming in
    assert zoomed_in_position < initial_position, (
        f"Expected X position after zoom-in to be greater than {initial_position}, "
        f"but got {zoomed_in_position}"
    )

    # Reset zoom to 100% using the "zoom-reset" control
    panel.click_on("zoom-reset")
    reset_position = _get_div_x_position(driver)
    logging.info(f"X position of div after zoom-reset: {reset_position}")

    # Assert that the X-coordinate after reset is back to the initial value
    assert reset_position == initial_position, (
        f"Expected X position after zoom-reset to be {initial_position}, but got {reset_position}"
    )

    # Zoom out using the "zoom-reduce" control
    panel.click_on("zoom-reduce")
    zoomed_out_position = _get_div_x_position(driver)
    logging.info(f"X position of div after zoom-out: {zoomed_out_position}")

    # Check zoom level in the toolbar
    nav.element_attribute_contains(
        "toolbar-zoom-level",
        attr_name="label",
        attr_value=EXPECTED_ZOOM_OUT_LABEL,
    )

    # Assert that the X-coordinate decreases after zooming out
    assert zoomed_out_position > initial_position, (
        f"Expected X position after zoom-out to be less than {initial_position}, "
        f"but got {zoomed_out_position}"
    )

    # Revert zoom settings to 100%
    panel.click_on("zoom-reset")
