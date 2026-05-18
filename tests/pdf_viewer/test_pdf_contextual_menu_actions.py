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


def test_pdf_context_menu_actions(driver: Firefox, pdf_viewer: GenericPdf):
    """
    C1017607: Verify that context menu actions apply to PDF form input fields
    """
    context_menu = ContextMenu(driver)
    util = Utilities()
    random_text = util.generate_random_text("word")

    # Step 1: PDF form with text and numeric fields is opened by the pdf_viewer fixture.
    pdf_viewer.element_visible(TEXT_FIELD)
    pdf_viewer.element_visible(NUMERIC_FIELD)

    # Step 2: Enter text in the text field.
    pdf_viewer.fill(TEXT_FIELD, random_text, press_enter=False)
    pdf_viewer.element_attribute_is(TEXT_FIELD, "value", random_text)

    # Step 3: Use the context menu copy and paste actions on the text field.
    pdf_viewer.triple_click(TEXT_FIELD)
    pdf_viewer.context_click(TEXT_FIELD)
    context_menu.click_and_hide_menu("context-menu-copy")

    pdf_viewer.get_element(TEXT_FIELD).clear()
    pdf_viewer.element_attribute_is(TEXT_FIELD, "value", "")

    pdf_viewer.context_click(TEXT_FIELD)
    context_menu.click_and_hide_menu("context-menu-paste")
    pdf_viewer.element_attribute_is(TEXT_FIELD, "value", random_text)

    # Step 4: Use the context menu cut and paste actions on the text field.
    pdf_viewer.triple_click(TEXT_FIELD)
    pdf_viewer.context_click(TEXT_FIELD)
    context_menu.click_and_hide_menu("context-menu-cut")
    pdf_viewer.element_attribute_is(TEXT_FIELD, "value", "")

    pdf_viewer.context_click(TEXT_FIELD)
    context_menu.click_and_hide_menu("context-menu-paste")
    pdf_viewer.element_attribute_is(TEXT_FIELD, "value", random_text)

    # Step 5: Use the context menu delete action on the text field.
    pdf_viewer.triple_click(TEXT_FIELD)
    pdf_viewer.context_click(TEXT_FIELD)
    context_menu.click_and_hide_menu("context-menu-delete-in-form")
    pdf_viewer.element_attribute_is(TEXT_FIELD, "value", "")

    # Step 6: Enter numbers in the numeric field.
    pdf_viewer.fill_element(NUMERIC_FIELD, NUMERIC_TEXT)
    pdf_viewer.element_attribute_is(NUMERIC_FIELD, "value", NUMERIC_TEXT)

    # Step 7: Use the context menu copy and paste actions on the numeric field.
    pdf_viewer.triple_click(NUMERIC_FIELD)
    pdf_viewer.context_click(NUMERIC_FIELD)
    context_menu.click_and_hide_menu("context-menu-copy")

    pdf_viewer.get_element(NUMERIC_FIELD).clear()
    pdf_viewer.element_attribute_is(NUMERIC_FIELD, "value", "")

    pdf_viewer.context_click(NUMERIC_FIELD)
    context_menu.click_and_hide_menu("context-menu-paste")
    pdf_viewer.element_attribute_is(NUMERIC_FIELD, "value", NUMERIC_TEXT)

    # Step 8: Use the context menu cut and paste actions on the numeric field.
    pdf_viewer.triple_click(NUMERIC_FIELD)
    pdf_viewer.context_click(NUMERIC_FIELD)
    context_menu.click_and_hide_menu("context-menu-cut")
    pdf_viewer.element_attribute_is(NUMERIC_FIELD, "value", "")

    pdf_viewer.context_click(NUMERIC_FIELD)
    context_menu.click_and_hide_menu("context-menu-paste")
    pdf_viewer.element_attribute_is(NUMERIC_FIELD, "value", NUMERIC_TEXT)

    # Step 9: Use the context menu delete action on the numeric field.
    pdf_viewer.triple_click(NUMERIC_FIELD)
    pdf_viewer.context_click(NUMERIC_FIELD)
    context_menu.click_and_hide_menu("context-menu-delete-in-form")
    pdf_viewer.element_attribute_is(NUMERIC_FIELD, "value", "")
