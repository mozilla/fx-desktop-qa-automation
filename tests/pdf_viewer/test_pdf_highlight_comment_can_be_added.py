import pytest

from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"
COMMENT = "Highlight comment"


@pytest.fixture()
def test_case():
    return "3136668"

@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


@pytest.fixture()
def add_to_prefs_list():
    return [("pdfjs.annotationEditorMode", 0)]


def test_pdf_highlight_comment_can_be_added(pdf_viewer: GenericPdf):
    """C3136668: A comment can be added to highlighted PDF text."""
    pdf_viewer.element_visible("toolbar-highlight")
    pdf_viewer.highlight_pdf_text()
    pdf_viewer.add_comment_to_selected_highlight(COMMENT)
    assert pdf_viewer.get_element("highlight-comment-indicator").is_displayed(), (
        "Expected the saved comment to remain linked to the PDF highlight."
    )
