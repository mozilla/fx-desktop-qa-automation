import re

import pytest
from selenium.webdriver.support.color import Color

from modules.page_object import GenericPdf


@pytest.fixture()
def test_case():
    return "3969289"


@pytest.fixture(
    params=["boeing_brochure.pdf", "i-9.pdf", "interactiveform_enabled.pdf"]
)
def file_name(request):
    return request.param


@pytest.fixture()
def add_to_prefs_list():
    return [("pdfjs.enableSplitMerge", True), ("dom.disable_beforeunload", True)]


@pytest.mark.parametrize("selection_size", [1, 2], ids=["single", "multiple"])
def test_pdf_page_actions_across_document_types(
    pdf_viewer: GenericPdf, selection_size: int
):
    """C3969289: Select, copy/paste, and reorder pages in brochure and form PDFs."""
    # Step 1: Open a local PDF and record the pages to copy.
    assert pdf_viewer.max_page >= selection_size, (
        "The PDF must contain enough pages for the requested selection."
    )
    selected_numbers = list(range(1, selection_size + 1))
    selected_text = [pdf_viewer.get_page_text(number) for number in selected_numbers]
    pdf_viewer.jump_to_page(1)

    # Step 2: Open Pages and record the original thumbnail order.
    if (
        pdf_viewer.get_element("pages-sidebar-toggle").get_attribute("aria-expanded")
        != "true"
    ):
        pdf_viewer.click_on("pages-sidebar-toggle")
    original_pages = pdf_viewer.get_elements("page-thumbnails")
    assert len(original_pages) == pdf_viewer.max_page, (
        "The sidebar should contain a thumbnail for every document page."
    )

    # Step 3: Check one or multiple pages and verify the exact selection.
    pdf_viewer.select_pdf_pages(selected_numbers)
    selected_checkboxes = [
        pdf_viewer.get_element("page-thumbnail-checkbox", labels=[str(number)])
        for number in selected_numbers
    ]
    assert pdf_viewer.get_elements("selected-page-checkboxes") == selected_checkboxes, (
        "Only the requested page checkboxes should be selected."
    )

    # Step 4: Copy via Manage, paste after the selection, and verify the copied content.
    pdf_viewer.click_on("manage-dropdown-button")
    pdf_viewer.click_on("manage-copy-option")
    pdf_viewer.click_on("paste-after-page-button", labels=[str(selection_size)])
    pdf_viewer.wait.until(
        lambda _: len(pdf_viewer.get_elements("page-thumbnails"))
        == len(original_pages) + selection_size,
        message="Copy/paste should add exactly the selected number of pages.",
    )
    pages_after_copy = pdf_viewer.get_elements("page-thumbnails")
    assert pages_after_copy[:selection_size] == original_pages[:selection_size], (
        "Copying should preserve the original selected pages."
    )
    assert pages_after_copy[2 * selection_size :] == original_pages[selection_size:], (
        "Copying should preserve the order of all unselected pages."
    )
    for number, expected_text in enumerate(selected_text, start=selection_size + 1):
        assert pdf_viewer.get_page_text(number) == expected_text, (
            f"Pasted page {number} should match its selected source page."
        )

    # Step 5: Reselect the original pages and drag them after the first pasted page.
    pdf_viewer.jump_to_page(1)
    pdf_viewer.select_pdf_pages(selected_numbers)
    source = pdf_viewer.get_element("page-thumbnail-image", labels=["1"])
    target = pdf_viewer.get_element(
        "page-thumbnail-image", labels=[str(selection_size + 1)]
    )
    try:
        pdf_viewer.actions.move_to_element(source).click_and_hold().move_by_offset(
            0, 15
        ).perform()
        # Drop in the lower half without moving below the viewport edge.
        pdf_viewer.actions.move_to_element_with_offset(
            target, 0, int(target.size["height"] / 4)
        ).perform()
        pdf_viewer.element_visible("page-drop-guide")
        guide = pdf_viewer.get_element("page-drop-guide")
        guide_color = Color.from_string(guide.value_of_css_property("border-top-color"))
        assert guide_color.blue > guide_color.red, "The drop guide should be blue."
        assert (
            float(guide.value_of_css_property("border-top-width").removesuffix("px"))
            > 0
        ), "The drop guide should have a visible border."
        assert guide.rect["y"] >= target.rect["y"] + target.rect["height"], (
            "The guide should indicate a drop after the first pasted page."
        )
        preview = source
        if selection_size > 1:
            preview = pdf_viewer.get_element("dragged-page-group")
            assert preview.get_attribute("data-multiple-count") == str(
                selection_size
            ), "The drag preview should contain every selected page."
        colors = re.findall(
            r"rgba?\([^)]+\)", preview.value_of_css_property("box-shadow")
        )
        assert any(
            Color.from_string(value).blue > Color.from_string(value).red
            for value in colors
        ), "The dragged pages should have a blue highlight."
    finally:
        pdf_viewer.actions.release().perform()

    expected_pages = [
        pages_after_copy[selection_size],
        *pages_after_copy[:selection_size],
        *pages_after_copy[selection_size + 1 :],
    ]
    pdf_viewer.wait.until(
        lambda _: pdf_viewer.get_elements("page-thumbnails") == expected_pages,
        message="Only the selected pages should move together to the indicated position.",
    )
    assert pdf_viewer.get_elements("focused-page-thumbnail") == [original_pages[0]], (
        "Focus should remain on the first selected page after dropping."
    )
    assert [page.get_attribute("page-number") for page in expected_pages] == [
        str(number) for number in range(1, len(expected_pages) + 1)
    ], "Page numbers should reflect the new document order."
    for number, expected_text in enumerate(selected_text, start=2):
        assert pdf_viewer.get_page_text(number) == expected_text, (
            f"Moved page {number} should retain its original content."
        )
