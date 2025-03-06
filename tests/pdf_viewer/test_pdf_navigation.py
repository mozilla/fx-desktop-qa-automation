from typing import Literal

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.page_object import GenericPdf
from modules.util import Utilities

DOWNWARD = {Keys.DOWN, Keys.RIGHT, Keys.END, "next"}


@pytest.fixture()
def test_case():
    return "3927"


def move_pdf(pdf_viewer: GenericPdf, key: str | int) -> int:
    """
    Move pdf according to direction and key press.

    Arguments:
        pdf_viewer: Instance of generic pdf class
        key: which key is pressed on the pdf body

    Returns:
        the distance the page moved.
    """
    page_one_item = pdf_viewer.get_element("page-one-item")
    initial_location = page_one_item.location["y"]

    if key in Keys.__dict__.values():
        pdf_viewer.navigate_page_by_keys(key)
    elif isinstance(key, int):
        pdf_viewer.jump_to_page(key)
    else:
        pdf_viewer.navigate_page_by_scroll_key(key)

    # wait for scrolling down
    pdf_viewer.wait.until(
        lambda _: page_one_item.location["y"] < initial_location
        if key in DOWNWARD or isinstance(key, int)
        else page_one_item.location["y"] > initial_location
    )

    # scroll down using right key
    return abs(page_one_item.location["y"] - initial_location)


def test_navigation_keys(driver: Firefox, pdf_viewer: GenericPdf):
    """
    C3927.1: ensure that you can navigate through a PDF using keys

    Arguments:
        pdf_viewer: instance of generic pdf with given pdf_file_path.
    """
    # scroll down using arrow down key
    down_key_difference = move_pdf(pdf_viewer, Keys.DOWN)

    # scroll down using right key
    right_key_difference = move_pdf(pdf_viewer, Keys.RIGHT)
    # assert right key moves more than down key
    assert right_key_difference > down_key_difference

    # scroll down using end key
    end_key_difference = move_pdf(pdf_viewer, Keys.END)
    # assert end key moves more than right key
    assert end_key_difference > right_key_difference

    # scroll up using Up key
    up_key_difference = move_pdf(pdf_viewer, Keys.UP)

    # scroll up using left key
    left_key_difference = move_pdf(pdf_viewer, Keys.LEFT)
    # assert left key moves more than up key
    assert left_key_difference > up_key_difference

    # scroll using home key
    home_key_difference = move_pdf(pdf_viewer, Keys.HOME)
    # assert home key moves more than left key
    assert home_key_difference > left_key_difference


def test_navigation_next_prev(driver: Firefox, pdf_viewer: GenericPdf):
    """
    C3927.2: ensure that you can navigate through a PDF using next and previous keys

    Arguments:
        pdf_viewer: instance of generic pdf with given pdf_file_path.
    """
    # go to next page.
    move_pdf(pdf_viewer, "next")
    # go back to original page.
    move_pdf(pdf_viewer, "prev")


def test_navigation_page_numbers(driver: Firefox, pdf_viewer: GenericPdf):
    """
    C3927.3: Ensure that you can navigate through a PDF using the numbers at the top.

    Arguments:
        pdf_viewer: instance of generic pdf with given pdf_file_path.
    """
    # get an element from page one
    page_one_item = pdf_viewer.get_element("page-one-item")
    original_position = page_one_item.location["y"]

    # jump to the second page and measure the delta
    one_page_delta = move_pdf(pdf_viewer, 2)

    # jump to fourth page and measure the delta
    two_page_delta = move_pdf(pdf_viewer, 4)

    # ensure that the jump for two pages was twice of the one page jump
    assert (2 * one_page_delta) - 10 <= two_page_delta <= (2 * one_page_delta) + 10

    # jump back to original position and ensure we are back where we started
    pdf_viewer.jump_to_page(1)
    first_page_position = page_one_item.location["y"]
    assert first_page_position == original_position


def test_toolbar_options_cursor(driver: Firefox, pdf_viewer: GenericPdf):
    """
    C3927.4: Ensure the correct cursor is displayed

    Arguments:
        pdf_viewer: instance of generic pdf with given pdf_file_path.
    """
    # open PDF and get body element
    body = pdf_viewer.get_element("pdf-body")

    # open the menu and get the current cursor
    pdf_viewer.select_toolbar_option("toolbar-hand-tool")
    cursor_style = driver.execute_script(
        "return window.getComputedStyle(arguments[0]).cursor;", body
    )

    assert cursor_style == "grab"

    # repeat with a different cursor
    pdf_viewer.select_toolbar_option("toolbar-select-tool")
    cursor_style = driver.execute_script(
        "return window.getComputedStyle(arguments[0]).cursor;", body
    )

    assert cursor_style == "auto"


def test_toolbar_options_rotate(driver: Firefox, pdf_viewer: GenericPdf):
    """
    C3927.5: Ensure the correct rotation is shown

    Arguments:
        pdf_viewer: instance of generic pdf with given pdf_file_path.
    """
    for i in range(1, 4):
        pdf_viewer.select_toolbar_option("toolbar-rotate-cw")
        element = pdf_viewer.get_element("pdf-text-layer")
        pdf_viewer.wait.until(
            lambda _: int(element.get_attribute("data-main-rotation")) == i * 90
        )
    # rotate clockwise

    # rotate counterclockwise
    pdf_viewer.select_toolbar_option("toolbar-rotate-ccw")
    element = pdf_viewer.get_element("pdf-text-layer")
    pdf_viewer.wait.until(
        lambda _: element.get_attribute("data-main-rotation") == "180"
    )
