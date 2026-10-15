import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu
from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"
TEXT_TO_ADD = "PDF editor text"


@pytest.fixture()
def test_case():
    return "1938271"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


@pytest.fixture()
def add_to_prefs_list():
    return [("pdfjs.annotationEditorMode", 0)]


def _assert_text_areas(pdf_viewer: GenericPdf, expected_count: int) -> None:
    pdf_viewer.wait_for_pdf_text_area_count(expected_count)
    expected_values = [TEXT_TO_ADD] * expected_count
    pdf_viewer.expect(
        lambda _: (
            [element.text for element in pdf_viewer.get_elements("added-text")]
            == expected_values
        )
    )
    text_values = [element.text for element in pdf_viewer.get_elements("added-text")]
    assert text_values == expected_values, (
        f"Expected {expected_count} PDF text areas containing '{TEXT_TO_ADD}', "
        f"got {text_values}."
    )


@pytest.mark.headed
def test_pdf_text_can_be_copied_cut_and_pasted_from_context_menu(
    driver: Firefox, pdf_viewer: GenericPdf
):
    """C1938271: Copy, cut, and paste PDF text from context menus."""
    context_menu = ContextMenu(driver)

    pdf_viewer.element_visible("toolbar-text")
    pdf_viewer.select_editor_tool("toolbar-text")
    pdf_viewer.add_text_to_pdf_page(TEXT_TO_ADD)

    pdf_viewer.select_pdf_text_area()
    pdf_viewer.context_click("added-text-content")
    context_menu.element_clickable("pdfjs-copy")
    context_menu.click_and_hide_menu("pdfjs-copy")

    pdf_page = pdf_viewer.get_element("pdf-page", labels=["1"])
    pdf_viewer.context_click(pdf_page)
    context_menu.element_clickable("pdfjs-paste")
    context_menu.click_and_hide_menu("pdfjs-paste")
    _assert_text_areas(pdf_viewer, 2)

    pdf_viewer.select_pdf_text_area()
    pdf_viewer.context_click("added-text-content")
    context_menu.element_clickable("pdfjs-cut")
    context_menu.click_and_hide_menu("pdfjs-cut")
    _assert_text_areas(pdf_viewer, 1)

    pdf_viewer.clear_cache()
    pdf_page = pdf_viewer.get_element("pdf-page", labels=["1"])
    pdf_viewer.context_click(pdf_page)
    context_menu.element_clickable("pdfjs-paste")
    context_menu.click_and_hide_menu("pdfjs-paste")
    _assert_text_areas(pdf_viewer, 2)
