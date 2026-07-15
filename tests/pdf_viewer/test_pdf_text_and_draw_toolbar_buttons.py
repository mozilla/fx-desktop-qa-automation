import pytest

from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"
TEXT_TO_ADD = "PDF editor text"


@pytest.fixture()
def test_case():
    return "1938254"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


@pytest.fixture()
def add_to_prefs_list():
    return [("pdfjs.annotationEditorMode", 0)]


def test_pdf_text_and_draw_toolbar_buttons(pdf_viewer: GenericPdf):
    """
    C1938254: Verify that editing PDF document using Text and Draw buttons
    from toolbar works as expected.
    """
    # Step 1: PDF is opened and Text/Draw toolbar buttons are available.
    pdf_viewer.element_visible("toolbar-draw")
    pdf_viewer.element_visible("toolbar-text")

    # Step 2-3: Select Draw and draw on the PDF document.
    pdf_viewer.select_editor_tool("toolbar-draw")
    pdf_viewer.draw_on_pdf_page()

    # Step 4-5: Select Text and add text on the PDF document.
    pdf_viewer.select_editor_tool("toolbar-text")
    pdf_viewer.add_text_to_pdf_page(TEXT_TO_ADD)
