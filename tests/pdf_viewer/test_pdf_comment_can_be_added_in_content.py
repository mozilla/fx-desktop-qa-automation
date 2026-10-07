import pytest

from modules.page_object import GenericPdf

COMMENT = "Comment added from the text selection"


@pytest.fixture()
def test_case():
    return "3139940"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return "i-9.pdf"


@pytest.fixture()
def add_to_prefs_list():
    return [("pdfjs.annotationEditorMode", 0)]


def test_pdf_comment_can_be_added_in_content(pdf_viewer: GenericPdf):
    """C3139940: Add a comment directly from a PDF text selection."""
    # Step 1: The fixture opens the local PDF with the editing tools inactive.
    text = pdf_viewer.get_first_text_element()

    # Step 2: Select a word without first applying a highlight.
    pdf_viewer.double_click(text)
    pdf_viewer.element_visible("selection-comment-button")
    assert not pdf_viewer.get_elements("added-highlight")

    # Step 3: The in-content Comment button highlights the selection and opens input.
    pdf_viewer.click_on("selection-comment-button")
    pdf_viewer.element_visible("added-highlight")
    highlight = pdf_viewer.get_element("added-highlight")
    original_rect = highlight.rect
    pdf_viewer.element_visible("comment-dialog")
    pdf_viewer.element_attribute_is("comment-input", "value", "")

    # Step 4: Add the message and reopen it to verify its link to the same highlight.
    pdf_viewer.fill("comment-input", COMMENT, press_enter=False)
    pdf_viewer.click_on("comment-save")
    pdf_viewer.element_not_visible("comment-dialog")
    pdf_viewer.element_visible("highlight-comment-indicator")
    assert pdf_viewer.get_elements("added-highlight") == [highlight]
    assert highlight.rect == original_rect
    pdf_viewer.click_on("comment-indicator")
    pdf_viewer.element_visible("comment-popup-text")
    assert pdf_viewer.get_element("comment-popup-text").text == COMMENT
