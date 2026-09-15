import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu
from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"


@pytest.fixture()
def test_case():
    return "1938264"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


@pytest.fixture()
def add_to_prefs_list():
    return [("pdfjs.annotationEditorMode", 0)]


@pytest.mark.headed
def test_pdf_drawing_can_be_copied_cut_and_pasted_from_context_menu(
    driver: Firefox, pdf_viewer: GenericPdf
):
    """C1938264: Copy, cut, and paste a PDF drawing from context menus."""
    context_menu = ContextMenu(driver)

    pdf_viewer.element_visible("toolbar-draw")
    pdf_viewer.select_editor_tool("toolbar-draw")
    pdf_viewer.draw_on_pdf_page()

    drawing_area = pdf_viewer.select_drawing_area()
    pdf_viewer.context_click(drawing_area)
    context_menu.click_and_hide_menu("pdfjs-copy")

    pdf_page = pdf_viewer.get_element("pdf-page", labels=["1"])
    pdf_viewer.context_click(pdf_page)
    context_menu.click_and_hide_menu("pdfjs-paste")
    pdf_viewer.wait_for_drawing_path_count(2)

    drawing_area = pdf_viewer.select_drawing_area()
    pdf_viewer.context_click(drawing_area)
    context_menu.click_and_hide_menu("pdfjs-cut")
    pdf_viewer.wait_for_drawing_path_count(1)

    pdf_viewer.clear_cache()
    pdf_page = pdf_viewer.get_element("pdf-page", labels=["1"])
    pdf_viewer.context_click(pdf_page)
    context_menu.click_and_hide_menu("pdfjs-paste")
    pdf_viewer.wait_for_drawing_path_count(2)
