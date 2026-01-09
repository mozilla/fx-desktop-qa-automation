import logging

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object_menu_bar import MenuBar
from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "165060"


EXPECTED_ZOOM_IN_LABEL = "110%"
EXPECTED_ZOOM_OUT_LABEL = "90%"

TEST_PAGE = "https://www.example.com"


def _get_div_x_position(driver: Firefox) -> int:
    """
    Returns the X location of the first <div> element on the page.
    """
    div = driver.find_element(By.TAG_NAME, "div")
    return int(div.location["x"])


def _open_view_zoom_menu_zoom_in(menu_bar: MenuBar) -> None:
    """
    Open View > Zoom > Zoom In
    """
    menu_bar.activate_menu_bar()
    menu_bar.open_menu("View")
    menu_bar.click_on("menu-bar-zoom")
    menu_bar.click_and_hide_menu("menu-bar-zoom-enlarge")


def _zoom_reset(menu_bar: MenuBar) -> None:
    """
    Performs View > Zoom > Reset.
    """
    menu_bar.click_on("menu-bar-zoom")
    menu_bar.click_and_hide_menu("menu-bar-zoom-reset")

    # Reset the zoom level back to 100%
    menu_bar.click_on("menu-bar-zoom")
    menu_bar.click_and_hide_menu("menu-bar-zoom-reset")
    menu_bar.click_and_hide_menu("view-menu-button")


def _zoom_out(menu_bar: MenuBar) -> None:
    """
    Performs View > Zoom > Zoom Out.
    """
    menu_bar.click_on("menu-bar-zoom")
    menu_bar.click_and_hide_menu("menu-bar-zoom-reduce")


def test_zoom_from_menu_bar(driver: Firefox):
    """
    This test verifies that the X-coordinate of a <div> element's position
    changes appropriately when zooming in, resetting zoom, and zooming out
    using the Firefox menu bar controls. Additionally, it checks that the zoom
    level indicator updates correctly.
    """

    # Open the test page and record the initial position of the <div>
    page = GenericPage(driver, url=TEST_PAGE)
    page.open()

    initial_position = _get_div_x_position(driver)
    logging.info(f"Initial X position of div: {initial_position}")

    # Access the zoom menu and zoom in
    menu_bar = MenuBar(driver)
    _open_view_zoom_menu_zoom_in(menu_bar)

    # Wait for zoom to apply and get the new position of the <div>
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

    # Reset Zoom to 100%
    _zoom_reset(menu_bar)

    # Wait for zoom reset to apply and get the reset position of the <div>
    reset_position = _get_div_x_position(driver)
    logging.info(f"X position of div after zoom-reset: {reset_position}")

    # Check that the zoom button no longer exists
    nav.element_not_visible("toolbar-zoom-level")

    # Assert that the X-coordinate after reset is back to the initial value
    assert reset_position == initial_position, (
        f"Expected X position after zoom-reset to be {initial_position}, but got {reset_position}"
    )

    # Assert that the X-coordinate after reset is back to the initial value
    assert reset_position == initial_position, (
        f"Expected X position after zoom-reset to be {initial_position}, but got {reset_position}"
    )

    # Zoom Out
    _zoom_out(menu_bar)

    # Wait for zoom out to apply and get the new position of the <div>
    zoomed_out_position = _get_div_x_position(driver)
    logging.info(f"X position of div after zoom-out: {zoomed_out_position}")

    # Check zoom level in the toolbar
    nav.element_attribute_contains(
        name="toolbar-zoom-level",
        attr_name="label",
        attr_value=EXPECTED_ZOOM_OUT_LABEL,
    )

    # Assert that the X-coordinate decreases after zooming out
    assert zoomed_out_position > reset_position, (
        f"Expected X position after zoom-out to be less than {reset_position}, "
        f"but got {zoomed_out_position}"
    )

    # Reset the zoom level back to 100% and close menu
    _zoom_reset(menu_bar)
    menu_bar.click_and_hide_menu("view-menu-button")
