import pytest
from selenium.webdriver.common.keys import Keys

from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"
TEXT_FIELD = "first-name-field"
NUMERIC_FIELD = "zipcode-field"
INITIAL_TEXT = "John"
MODIFIED_TEXT = "John Doe"
INITIAL_NUMBER = "12345"
MODIFIED_NUMBER = "54321"
PASTED_TEXT = " Test"


@pytest.fixture()
def test_case():
    return "1020324"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


def _modify_field_and_verify(
    pdf_viewer: GenericPdf,
    field: str,
    initial_value: str,
    modified_value: str,
):
    # Enter data and click outside the field to verify the value is saved.
    pdf_viewer.fill(field, initial_value, press_enter=False)
    pdf_viewer.fill_element(field, Keys.TAB)
    pdf_viewer.element_attribute_is(field, "value", initial_value)

    # Edit the previous value and click outside the field to verify the edit is saved.
    pdf_viewer.click_on(field)
    pdf_viewer.triple_click(field)
    pdf_viewer.fill_element(field, modified_value + Keys.TAB)
    pdf_viewer.element_attribute_is(field, "value", modified_value)

    return modified_value


def test_pdf_modify_text_number_data(pdf_viewer: GenericPdf):
    """
    C1020324: Verify that modifying text/number data in fields correctly works.
    """
    # Step 1: PDF form with text and numeric fields is opened by the pdf_viewer fixture.
    pdf_viewer.element_visible(TEXT_FIELD)
    pdf_viewer.element_visible(NUMERIC_FIELD)

    # Steps 2-7: Enter, modify, copy/paste, and verify text and numeric field values.
    saved_text = _modify_field_and_verify(
        pdf_viewer, TEXT_FIELD, INITIAL_TEXT, MODIFIED_TEXT
    )
    _modify_field_and_verify(pdf_viewer, NUMERIC_FIELD, INITIAL_NUMBER, MODIFIED_NUMBER)

    # Copy and paste text inside the previously edited field, then verify it remains.
    pdf_viewer.fill(TEXT_FIELD, PASTED_TEXT, press_enter=False)
    pdf_viewer.triple_click(TEXT_FIELD)
    pdf_viewer.copy()
    pdf_viewer.fill(TEXT_FIELD, saved_text, press_enter=False)
    pdf_viewer.fill_element(TEXT_FIELD, Keys.END)
    pdf_viewer.paste()
    pdf_viewer.fill_element(TEXT_FIELD, Keys.TAB)
    pdf_viewer.element_attribute_is(TEXT_FIELD, "value", saved_text + PASTED_TEXT)
