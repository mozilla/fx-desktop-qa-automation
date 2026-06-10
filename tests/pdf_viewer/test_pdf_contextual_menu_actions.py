import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu
from modules.page_object import GenericPdf
from modules.util import Utilities

PDF_FILE_NAME = "i-9.pdf"
NUMERIC_TEXT = "12345"
TEXT_FIELD = "first-name-field"
NUMERIC_FIELD = "zipcode-field"


@pytest.fixture()
def test_case():
    return "1017607"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


def _verify_context_menu_actions(
    pdf_viewer: GenericPdf,
    context_menu: ContextMenu,
    field: str,
    value: str,
):
    pdf_viewer.fill(field, value, press_enter=False)
    pdf_viewer.element_attribute_is(field, "value", value)

    # Verify context menu copy and paste.
    pdf_viewer.triple_click(field)
    pdf_viewer.context_click(field)
    context_menu.click_and_hide_menu("context-menu-copy")

    pdf_viewer.get_element(field).clear()
    pdf_viewer.element_attribute_is(field, "value", "")

    pdf_viewer.context_click(field)
    context_menu.click_and_hide_menu("context-menu-paste")
    pdf_viewer.element_attribute_is(field, "value", value)

    # Verify context menu cut and paste.
    pdf_viewer.triple_click(field)
    pdf_viewer.context_click(field)
    context_menu.click_and_hide_menu("context-menu-cut")
    pdf_viewer.element_attribute_is(field, "value", "")

    pdf_viewer.context_click(field)
    context_menu.click_and_hide_menu("context-menu-paste")
    pdf_viewer.element_attribute_is(field, "value", value)

    # Verify context menu delete.
    pdf_viewer.triple_click(field)
    pdf_viewer.context_click(field)
    context_menu.click_and_hide_menu("context-menu-delete-in-form")
    pdf_viewer.element_attribute_is(field, "value", "")


def test_pdf_contextual_menu_actions(driver: Firefox, pdf_viewer: GenericPdf):
    """
    C1017607: Verify that context menu actions apply to PDF form input fields
    """
    context_menu = ContextMenu(driver)
    util = Utilities()
    random_text = util.generate_random_text("word")

    # Step 1: PDF form with text and numeric fields is opened by the pdf_viewer fixture.
    pdf_viewer.element_visible(TEXT_FIELD)
    pdf_viewer.element_visible(NUMERIC_FIELD)

    # Step 2: Enter text and numbers in both text and numeric fields.
    _verify_context_menu_actions(pdf_viewer, context_menu, TEXT_FIELD, random_text)
    _verify_context_menu_actions(pdf_viewer, context_menu, NUMERIC_FIELD, NUMERIC_TEXT)
