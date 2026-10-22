import math

import pytest
from selenium.webdriver.support.color import Color

from modules.page_object import GenericPdf


@pytest.fixture()
def test_case():
    return "3969292"


@pytest.fixture()
def add_to_prefs_list():
    return [("pdfjs.enableSplitMerge", True)]


def test_pdf_sidebar_resize_maximized(pdf_viewer: GenericPdf):
    """C3969292: Resize Pages in a maximized window and reflow thumbnails."""
    # Step 1: The fixture opens the suite's local multipage PDF.
    assert pdf_viewer.max_page >= 4, (
        "The PDF should have enough pages to verify multiple thumbnail columns."
    )

    # Step 2: Open the Pages sidebar and retain every thumbnail's identity.
    pdf_viewer.click_on("pages-sidebar-toggle")
    pdf_viewer.element_visible("page-thumbnail-image", labels=["1"])
    sidebar = pdf_viewer.get_element("pages-sidebar")
    resizer = pdf_viewer.get_element("pages-sidebar-resizer")
    container = pdf_viewer.get_element("page-thumbnails-container")
    pages = pdf_viewer.get_elements("page-thumbnails")
    assert len(pages) == pdf_viewer.max_page, (
        "The sidebar should contain a thumbnail for every PDF page."
    )

    # Step 3: Maximize Firefox before testing sidebar resizing.
    pdf_viewer.driver.maximize_window()
    maximized_rect = pdf_viewer.driver.get_window_rect()
    initial_width = sidebar.rect["width"]

    # Step 4: Hover beside the scrollbar and verify the blue resize guide.
    pdf_viewer.actions.move_to_element(resizer).perform()

    def blue_guide(_):
        color = Color.from_string(resizer.value_of_css_property("background-color"))
        return color.blue > color.red and float(color.alpha) > 0

    pdf_viewer.wait.until(
        blue_guide, message="Hovering should show a blue resize guide."
    )
    assert resizer.value_of_css_property("cursor") == "ew-resize", (
        "The sidebar edge should show the horizontal resize cursor."
    )

    # Step 5: Widen to the maximum, then narrow and verify packed thumbnail columns.
    initial_columns = sum(
        abs(page.rect["y"] - pages[0].rect["y"]) < 2 for page in pages
    )
    # Read the content viewport because WebDriver window size includes browser chrome.
    viewport_width = pdf_viewer.driver.execute_script("return window.innerWidth;")
    right_offset = int(viewport_width - resizer.rect["x"] - resizer.rect["width"] - 10)
    assert right_offset > 0, "The maximized window should allow widening the sidebar."
    column_counts = []
    for direction in ("right", "left"):
        previous_width = sidebar.rect["width"]
        offset = (
            right_offset
            if direction == "right"
            else -round(previous_width - initial_width)
        )
        try:
            pdf_viewer.actions.move_to_element(resizer).click_and_hold().move_by_offset(
                offset, 0
            ).perform()
        finally:
            pdf_viewer.actions.release().perform()
        pdf_viewer.wait.until(
            lambda _: sidebar.rect["width"] > previous_width + 10
            if direction == "right"
            else sidebar.rect["width"] < previous_width - 10,
            message=f"Dragging {direction} should change the sidebar width.",
        )
        width = container.rect["width"]
        padding = sum(
            float(container.value_of_css_property(f"padding-{side}").removesuffix("px"))
            for side in ("left", "right")
        )
        gap = float(container.value_of_css_property("column-gap").removesuffix("px"))
        thumbnail_width = pages[0].rect["width"]
        expected_columns = min(
            len(pages), math.floor((width - padding + gap) / (thumbnail_width + gap))
        )
        pdf_viewer.wait.until(
            lambda _: sum(
                abs(page.rect["y"] - pages[0].rect["y"]) < 2 for page in pages
            )
            == expected_columns,
            message=f"After resizing {direction}, thumbnails should fill all available columns.",
        )
        column_counts.append(expected_columns)
        assert pdf_viewer.get_elements("page-thumbnails") == pages, (
            "Resizing should preserve every page thumbnail and its document order."
        )
    assert column_counts[0] > initial_columns, (
        "Widening should increase the number of thumbnail columns."
    )
    assert column_counts[1] < column_counts[0], (
        "Narrowing should reduce the number of thumbnail columns."
    )
    assert pdf_viewer.driver.get_window_rect() == maximized_rect, (
        "Firefox should remain maximized throughout sidebar resizing."
    )
