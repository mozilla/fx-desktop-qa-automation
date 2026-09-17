import pytest

PDF_FILE_NAME = "i-9.pdf"
TEXT_TO_ADD = "PDF editor text"
TEXT_X_OFFSET = -120
TEXT_Y_OFFSET = -180


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


def test_user_can_select_location_for_pdf_text(pdf_viewer):
    """
    C1938265: Verify that the user can select a location for writing text
    over the PDF document.
    """
    pdf_viewer.element_visible("toolbar-text")
    pdf_viewer.element_visible("toolbar-draw")

    pdf_viewer.select_editor_tool("toolbar-text")
    pdf_viewer.add_text_to_pdf_page(
        TEXT_TO_ADD,
        x_offset=TEXT_X_OFFSET,
        y_offset=TEXT_Y_OFFSET,
    )
    pdf_viewer.expect_text_at_pdf_page_location()
