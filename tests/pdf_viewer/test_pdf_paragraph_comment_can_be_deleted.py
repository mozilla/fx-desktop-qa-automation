import pytest

from modules.page_object import GenericPdf

COMMENT = "Paragraph comment to delete"


@pytest.fixture()
def test_case():
    return "3139287"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return "i-9.pdf"


@pytest.fixture()
def add_to_prefs_list():
    return [("pdfjs.annotationEditorMode", 0)]


def test_pdf_paragraph_comment_can_be_deleted(pdf_viewer: GenericPdf):
    """C3139287: Deleting a comment preserves the highlight on its paragraph."""
    paragraph = pdf_viewer.get_element(
        "pdf-text-containing", labels=["START HERE: Employers must ensure"]
    )
    pdf_viewer.element_visible(paragraph)
    pdf_viewer.highlight_pdf_text(paragraph)
    highlight = pdf_viewer.get_element("added-highlight")
    original_rect = highlight.rect
    pdf_viewer.add_comment_to_selected_highlight(COMMENT)
    pdf_viewer.click_on("toolbar-highlight")
    pdf_viewer.element_visible("comment-indicator")
    pdf_viewer.click_on("comment-indicator")
    pdf_viewer.element_visible("comment-popup-text")
    assert pdf_viewer.get_element("comment-popup-text").text == COMMENT

    pdf_viewer.click_on("comment-popup-delete")
    pdf_viewer.element_not_visible("comment-popup-text")
    pdf_viewer.element_not_visible("comment-indicator")
    pdf_viewer.element_visible("added-highlight")
    assert pdf_viewer.get_elements("added-highlight") == [highlight], (
        "Deleting the comment should preserve the original highlight."
    )
    assert highlight.rect == original_rect, (
        "The highlight should remain on the same paragraph."
    )
