import pytest
from selenium.webdriver.common.keys import Keys

from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"


@pytest.fixture()
def test_case():
    return "1938263"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


@pytest.fixture()
def add_to_prefs_list():
    return [("pdfjs.annotationEditorMode", 0)]


def test_pdf_drawing_can_be_copied_cut_and_pasted_with_keyboard(
    pdf_viewer: GenericPdf,
):
    """C1938263: Copy, cut, and paste a PDF drawing with keyboard shortcuts."""
    pdf_viewer.element_visible("toolbar-draw")
    pdf_viewer.select_editor_tool("toolbar-draw")
    pdf_viewer.draw_on_pdf_page()

    pdf_viewer.select_drawing_area()
    pdf_viewer.perform_key_combo(Keys.CONTROL, "c")
    pdf_viewer.perform_key_combo(Keys.CONTROL, "v")
    pdf_viewer.wait_for_drawing_area_count(2)

    pdf_viewer.perform_key_combo(Keys.CONTROL, "x")
    pdf_viewer.wait_for_drawing_area_count(1)

    pdf_viewer.perform_key_combo(Keys.CONTROL, "v")
    pdf_viewer.wait_for_drawing_area_count(2)
