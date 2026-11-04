import re

import pytest
from auto_fxui.page_object import GenericPdf
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.color import Color

COMMENT = "Keep this comment with the original first page"
ADDED_TEXT = "Annotation on original page two"


@pytest.fixture()
def test_case():
    return "3969295"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("pdfjs.enableSplitMerge", True),
        ("pdfjs.annotationEditorMode", 0),
        ("dom.disable_beforeunload", True),
        ("browser.download.useDownloadDir", False),
    ]


def test_pdf_save_existing_annotations(
    pdf_viewer: GenericPdf, tmp_path, wait_for_file_download
):
    """C3969295: Existing annotations survive page moves, deletion, and saving."""

    def save_and_reopen(viewer, filename):
        saved_pdf = tmp_path / filename
        viewer.install_mock_file_picker(str(saved_pdf))
        try:
            viewer.click_download_button()
            viewer.wait_for_mock_file_picker()
        finally:
            viewer.cleanup_mock_file_picker()
        wait_for_file_download(saved_pdf)
        viewer.driver.switch_to.new_window("tab")
        return GenericPdf(viewer.driver, pdf_url=saved_pdf.as_uri())

    def annotation_positions(viewer, comment_page, text_page, saved=True):
        # A reopened file renders the edits as annotations instead of editors.
        # The text editor's padded box is larger than the saved annotation, so its
        # inner text box is used and only its position is compared.
        highlight, text = (
            ("saved-highlight", "saved-text")
            if saved
            else ("added-highlight", "added-text-content")
        )
        positions = {}
        for page_number, name, locator in (
            (comment_page, "highlight", highlight),
            (comment_page, "comment", "comment-indicator"),
            (text_page, "text", text),
        ):
            viewer.jump_to_page(page_number)
            # Page identities change on reorder; multiple lookups bypass element caching.
            page = viewer.get_elements("pdf-page", labels=[str(page_number)])[0]
            annotation = viewer.get_element(locator, parent_element=page)
            viewer.element_visible(annotation)
            page_rect = page.rect
            rect = annotation.rect
            positions[name] = {
                "x": (rect["x"] - page_rect["x"]) / page_rect["width"],
                "y": (rect["y"] - page_rect["y"]) / page_rect["height"],
            }
            if name != "text":
                positions[name]["width"] = rect["width"] / page_rect["width"]
                positions[name]["height"] = rect["height"] / page_rect["height"]
            if name == "comment":
                viewer.click_on(annotation)
                viewer.element_visible("comment-popup-text")
                assert viewer.get_element("comment-popup-text").text == COMMENT, (
                    "The comment should stay attached to the original first page."
                )
                viewer.perform_key_combo(Keys.ESCAPE)
                viewer.element_not_visible("comment-popup-text")
            elif name == "text":
                # textContent works for both editor text and transparent saved text.
                assert annotation.get_attribute("textContent") == ADDED_TEXT, (
                    "The text annotation should stay on the original second page."
                )
        return positions

    def check_annotations(viewer, comment_page, text_page, expected):
        actual = annotation_positions(viewer, comment_page, text_page)
        for name, position in expected.items():
            assert actual[name] == pytest.approx(position, abs=0.005), (
                f"The {name} should retain its position and size relative to its PDF page."
            )

    # Step 1: Open the local PDF and record distinct source-page text.
    original_count = pdf_viewer.max_page
    assert original_count >= 4, "The source PDF should contain at least four pages."
    original_text = [
        pdf_viewer.get_page_text(number) for number in range(1, original_count + 1)
    ]
    assert len(set(original_text)) == original_count, (
        "Source pages should have distinct text to verify their saved order."
    )

    # Step 2: Add a text comment and a text annotation on different pages, then save.
    pdf_viewer.jump_to_page(1)
    paragraph = pdf_viewer.get_element(
        "pdf-text-containing", labels=["Surplus machinery"]
    )
    pdf_viewer.highlight_pdf_text(paragraph)
    pdf_viewer.add_comment_to_selected_highlight(COMMENT)
    pdf_viewer.click_on("toolbar-highlight")
    pdf_viewer.jump_to_page(2)
    pdf_viewer.select_editor_tool("toolbar-text")
    pdf_viewer.add_text_to_pdf_page(
        ADDED_TEXT, page_number="2", x_offset=-100, y_offset=-100
    )
    pdf_viewer.perform_key_combo(Keys.ESCAPE)
    pdf_viewer.click_on("toolbar-text")
    original_positions = annotation_positions(pdf_viewer, 1, 2, saved=False)

    # Step 3: Reopen the saved copy in a new tab and activate Pages.
    saved_viewer = save_and_reopen(pdf_viewer, "existing-annotations.pdf")
    assert saved_viewer.max_page == original_count, (
        "The first save should preserve every source page."
    )
    check_annotations(saved_viewer, 1, 2, original_positions)
    saved_viewer.jump_to_page(1)
    saved_viewer.click_on("pages-sidebar-toggle")
    original_pages = saved_viewer.get_elements("page-thumbnails")

    # Step 4: Select both annotated pages using their checkboxes.
    saved_viewer.select_pdf_pages([1, 2])
    assert saved_viewer.get_elements("selected-page-checkboxes") == [
        saved_viewer.get_element("page-thumbnail-checkbox", labels=[str(number)])
        for number in (1, 2)
    ], "Exactly the two annotated pages should be selected."

    # Step 5: Move both pages after page three and verify drag feedback and order.
    # Dragging either selected page moves both. Page two is scrolled to the top so
    # the drop point stays clear of the sidebar's bottom edge, which autoscrolls.
    source = saved_viewer.get_element("page-thumbnail-image", labels=["2"])
    target = saved_viewer.get_element("page-thumbnail-image", labels=["3"])
    saved_viewer.scroll_to_element(source)
    try:
        saved_viewer.actions.move_to_element(source).click_and_hold().move_by_offset(
            0, 15
        ).perform()
        saved_viewer.actions.move_to_element_with_offset(
            target, 0, int(target.size["height"] / 4)
        ).perform()
        saved_viewer.element_visible("page-drop-guide")
        guide = saved_viewer.get_element("page-drop-guide")
        color = Color.from_string(guide.value_of_css_property("border-top-color"))
        assert color.blue > color.red, "The drop-location guide should be blue."
        assert (
            float(guide.value_of_css_property("border-top-width").removesuffix("px"))
            > 0
        ), "The drop-location guide should have a visible border."
        assert guide.rect["y"] >= target.rect["y"] + target.rect["height"], (
            "The drop guide should appear after page three."
        )
        group = saved_viewer.get_element("dragged-page-group")
        assert group.get_attribute("data-multiple-count") == "2", (
            "The drag preview should include both annotated pages."
        )
        colors = re.findall(
            r"rgba?\([^)]+\)", group.value_of_css_property("box-shadow")
        )
        assert any(
            Color.from_string(value).blue > Color.from_string(value).red
            for value in colors
        ), "The dragged page group should have a blue highlight."
    finally:
        saved_viewer.actions.release().perform()
    order = [3, 1, 2, *range(4, original_count + 1)]
    expected_pages = [original_pages[number - 1] for number in order]
    saved_viewer.wait.until(
        lambda _: saved_viewer.get_elements("page-thumbnails") == expected_pages,
        message="Both annotated pages should move together after original page three.",
    )
    assert saved_viewer.get_elements("focused-page-thumbnail") == [original_pages[0]], (
        "Focus should remain on the first selected page after the move."
    )
    assert [page.get_attribute("page-number") for page in expected_pages] == [
        str(number) for number in range(1, original_count + 1)
    ], "Page numbers should reflect the reordered document."
    check_annotations(saved_viewer, 2, 3, original_positions)

    # Step 6: Delete the unannotated last page, preserving the reordered pages.
    saved_viewer.select_pdf_pages([original_count])
    saved_viewer.click_on("manage-dropdown-button")
    saved_viewer.click_on("manage-delete-option")
    order.pop()
    saved_viewer.wait.until(
        lambda _: saved_viewer.get_elements("page-thumbnails") == expected_pages[:-1],
        message="Deleting the unannotated page should preserve the annotated pages.",
    )
    check_annotations(saved_viewer, 2, 3, original_positions)

    # Step 7: Save globally, reopen, and verify page contents and annotation positions.
    final_viewer = save_and_reopen(saved_viewer, "reordered-annotations.pdf")
    assert final_viewer.max_page == len(order), (
        "The final PDF should retain every remaining page and exclude the deleted page."
    )
    for number, original_number in enumerate(order, start=1):
        assert (
            final_viewer.get_page_text(number) == original_text[original_number - 1]
        ), f"Saved page {number} should contain original page {original_number}."
    check_annotations(final_viewer, 2, 3, original_positions)
