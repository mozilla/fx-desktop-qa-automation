import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu
from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"
DELETE_MENU_OPTION = "pdfjs-delete"


@pytest.fixture()
def test_case():
    return "1938259"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


@pytest.fixture()
def add_to_prefs_list():
    return [("pdfjs.annotationEditorMode", 0)]


def test_pdf_drawing_area_can_be_deleted_moved_or_resized(
    driver: Firefox, pdf_viewer: GenericPdf
):
    """
    C1938259: Verify that the drawing areas can be deleted, moved or resized.
    """
    context_menu = ContextMenu(driver)

    # Step 1: PDF is opened and the Draw toolbar button is available.
    pdf_viewer.element_visible("toolbar-draw")

    # Step 2: Select Draw and draw on the PDF document.
    pdf_viewer.select_editor_tool("toolbar-draw")
    pdf_viewer.draw_on_pdf_page()

    # Step 3: Verify the drawing area can be resized, moved, and deleted.
    drawing_area = pdf_viewer.select_drawing_area()
    pdf_viewer.resize_drawing_area(drawing_area)
    pdf_viewer.move_drawing_area(drawing_area)

    drawing_area = pdf_viewer.select_drawing_area()
    pdf_viewer.context_click(drawing_area)
    context_menu.click_and_hide_menu(DELETE_MENU_OPTION)
    pdf_viewer.element_does_not_exist("added-drawing")
