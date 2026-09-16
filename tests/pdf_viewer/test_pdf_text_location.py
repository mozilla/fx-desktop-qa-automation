import pytest

from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"
TEXT_TO_ADD = "PDF editor text"


@pytest.fixture()
def test_case():
    return "1938265"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


@pytest.fixture()
def add_to_prefs_list():
    return [("pdfjs.annotationEditorMode", 0)]


def test_user_can_select_location_for_pdf_text(pdf_viewer: GenericPdf):
    """
    C1938265: Verify that the user can select a location for writing text
    over the PDF document.
    """
    # Step 1: PDF is opened and the Text/Draw toolbar buttons are available.
    pdf_viewer.element_visible("toolbar-text")
    pdf_viewer.element_visible("toolbar-draw")

    # Steps 2-3: Select Text and add text at a location on the PDF document.
    pdf_viewer.select_editor_tool("toolbar-text")
    pdf_viewer.add_text_to_pdf_page(TEXT_TO_ADD)
