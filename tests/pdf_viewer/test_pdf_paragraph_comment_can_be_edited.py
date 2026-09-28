import pytest

from modules.page_object import GenericPdf

ORIGINAL_COMMENT = "Original paragraph comment"
EDITED_COMMENT = "Updated paragraph comment"


@pytest.fixture()
def test_case():
    return "3139285"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return "i-9.pdf"


@pytest.fixture()
def add_to_prefs_list():
    return [("pdfjs.annotationEditorMode", 0)]


def test_pdf_paragraph_comment_can_be_edited(pdf_viewer: GenericPdf):
    """C3139285: Editing a comment preserves its link to the PDF paragraph."""
    paragraph = pdf_viewer.get_element(
        "pdf-text-containing", labels=["START HERE: Employers must ensure"]
    )
    pdf_viewer.element_visible(paragraph)
    pdf_viewer.highlight_pdf_text(paragraph)
    highlight = pdf_viewer.get_element("added-highlight")
    original_rect = highlight.rect
    pdf_viewer.add_comment_to_selected_highlight(ORIGINAL_COMMENT)
    pdf_viewer.click_on("toolbar-highlight")
    pdf_viewer.element_visible("comment-indicator")
    pdf_viewer.click_on("comment-indicator")
    pdf_viewer.element_visible("comment-popup-text")
    assert pdf_viewer.get_element("comment-popup-text").text == ORIGINAL_COMMENT

    pdf_viewer.click_on("comment-popup-edit")
    pdf_viewer.element_visible("comment-dialog")
    pdf_viewer.element_attribute_is("comment-input", "value", ORIGINAL_COMMENT)
    pdf_viewer.fill("comment-input", EDITED_COMMENT, press_enter=False)
    pdf_viewer.click_on("comment-save")
    pdf_viewer.element_not_visible("comment-dialog")
    pdf_viewer.element_not_visible("comment-popup-text")

    assert pdf_viewer.get_elements("added-highlight") == [highlight], (
        "Editing the comment should preserve the original text annotation."
    )
    assert highlight.rect == original_rect, (
        "The text annotation should remain on the same paragraph."
    )
    pdf_viewer.click_on("comment-indicator")
    pdf_viewer.element_visible("comment-popup-text")
    assert pdf_viewer.get_element("comment-popup-text").text == EDITED_COMMENT, (
        "Reopening the original annotation should show the edited comment."
    )
