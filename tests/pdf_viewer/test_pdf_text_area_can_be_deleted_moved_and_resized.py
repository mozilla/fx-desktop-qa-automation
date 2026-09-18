import pytest

from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"
TEXT_TO_ADD = "PDF editor text"
UPDATED_FONT_SIZE = 24


@pytest.fixture()
def test_case():
    return "1938266"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


@pytest.fixture()
def add_to_prefs_list():
    return [("pdfjs.annotationEditorMode", 0)]


def test_pdf_text_area_can_be_deleted_moved_and_resized(pdf_viewer: GenericPdf):
    """C1938266: Delete, move, and resize text added to a PDF."""
    pdf_viewer.element_visible("toolbar-text")
    pdf_viewer.element_visible("toolbar-draw")

    pdf_viewer.select_editor_tool("toolbar-text")
    pdf_viewer.add_text_to_pdf_page(TEXT_TO_ADD)

    text_area = pdf_viewer.select_pdf_text_area()
    pdf_viewer.move_pdf_text_area(text_area)
    pdf_viewer.set_pdf_text_font_size(UPDATED_FONT_SIZE)
    pdf_viewer.delete_selected_pdf_text_area()
