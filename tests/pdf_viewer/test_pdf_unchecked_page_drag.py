import re

import pytest
from selenium.webdriver.support.color import Color

from modules.page_object import GenericPdf


@pytest.fixture()
def test_case():
    return "3969290"


@pytest.fixture()
def file_name():
    return "i-9.pdf"


@pytest.fixture()
def add_to_prefs_list():
    return [("pdfjs.enableSplitMerge", True), ("dom.disable_beforeunload", True)]


def test_pdf_unchecked_page_drag(pdf_viewer: GenericPdf):
    """C3969290: Drag one unchecked PDF page and verify the drop feedback and order."""
    # Step 1: The fixture opens a local multipage PDF with page organization enabled.
    assert pdf_viewer.max_page >= 2, "The document must contain at least two pages."

    # Step 2: Open Pages in the sidebar and record the original page order.
    pdf_viewer.click_on("pages-sidebar-toggle")
    pdf_viewer.element_visible("page-thumbnail-image", labels=["1"])
    original_pages = pdf_viewer.get_elements("page-thumbnails")
    source = pdf_viewer.get_element("page-thumbnail-image", labels=["1"])
    target = pdf_viewer.get_element("page-thumbnail-image", labels=["2"])

    assert not pdf_viewer.get_elements("selected-page-checkboxes"), (
        "No page checkbox should be checked before dragging."
    )

    # Step 3: Drag the unchecked first page below page two and verify drop feedback.
    source_rect = source.rect
    try:
        # Move beyond the viewer's drag threshold before approaching the drop target.
        pdf_viewer.actions.move_to_element(source).click_and_hold().move_by_offset(
            0, 15
        ).perform()
        pdf_viewer.actions.move_to_element_with_offset(
            target, 0, int(target.size["height"] / 2) + 15
        ).perform()
        pdf_viewer.element_visible("page-drag-placeholder")
        placeholder = pdf_viewer.get_element("page-drag-placeholder")
        assert placeholder.rect == pytest.approx(source_rect, abs=2), (
            "A placeholder should remain at the original page position."
        )
        pdf_viewer.element_visible("page-drop-guide")
        guide = pdf_viewer.get_element("page-drop-guide")
        guide_color = Color.from_string(guide.value_of_css_property("border-top-color"))
        assert guide_color.blue > guide_color.red, "The drop guide should be blue."
        assert (
            float(guide.value_of_css_property("border-top-width").removesuffix("px"))
            > 0
        ), "The drop guide must have a visible border."
        assert guide.rect["y"] >= target.rect["y"] + target.rect["height"], (
            "The drop guide should appear below the second page."
        )
        shadow_colors = re.findall(
            r"rgba?\([^)]+\)", source.value_of_css_property("box-shadow")
        )
        assert any(
            Color.from_string(value).blue > Color.from_string(value).red
            for value in shadow_colors
        ), "The dragged page should retain a blue highlight."
    finally:
        pdf_viewer.actions.release().perform()

    expected_pages = [original_pages[1], original_pages[0], *original_pages[2:]]
    pdf_viewer.expect(
        lambda _: pdf_viewer.get_elements("page-thumbnails") == expected_pages
    )
    assert pdf_viewer.get_elements("page-thumbnails") == expected_pages, (
        "Only the unchecked first page should move to the second position."
    )
    pdf_viewer.element_not_visible("page-drag-placeholder")
    pdf_viewer.element_not_visible("page-drop-guide")
