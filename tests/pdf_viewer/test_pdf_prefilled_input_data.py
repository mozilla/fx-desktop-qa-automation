import pytest
from selenium.webdriver.common.keys import Keys

from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"
FIRST_FIELD = "first-name-field"
SECOND_FIELD = "zipcode-field"
FIRST_FIELD_INITIAL_VALUE = "John"
SECOND_FIELD_INITIAL_VALUE = "12345"
APPENDED_TEXT = " Doe"
SECOND_FIELD_REPLACEMENT_VALUE = "54321"


@pytest.fixture()
def test_case():
    return "1019456"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


def test_pdf_prefilled_input_data(pdf_viewer: GenericPdf):
    """
    C1019456: Verify that input data in pre-filled fields works as expected.
    """
    # Step 1: PDF form with input fields is opened by the pdf_viewer fixture.
    pdf_viewer.element_visible(FIRST_FIELD)
    pdf_viewer.element_visible(SECOND_FIELD)

    # Pre-fill two input fields before verifying edit behavior.
    pdf_viewer.fill(FIRST_FIELD, FIRST_FIELD_INITIAL_VALUE, press_enter=False)
    pdf_viewer.element_attribute_is(FIRST_FIELD, "value", FIRST_FIELD_INITIAL_VALUE)

    pdf_viewer.fill(SECOND_FIELD, SECOND_FIELD_INITIAL_VALUE, press_enter=False)
    pdf_viewer.element_attribute_is(SECOND_FIELD, "value", SECOND_FIELD_INITIAL_VALUE)

    # Step 2-3: Click inside a pre-filled field and type more characters.
    pdf_viewer.click_on(FIRST_FIELD)
    pdf_viewer.fill_element(FIRST_FIELD, Keys.END + APPENDED_TEXT)
    pdf_viewer.element_attribute_is(
        FIRST_FIELD, "value", FIRST_FIELD_INITIAL_VALUE + APPENDED_TEXT
    )

    # Step 4: Click another pre-filled field and verify the first value remains.
    pdf_viewer.click_on(SECOND_FIELD)
    pdf_viewer.element_attribute_is(
        FIRST_FIELD, "value", FIRST_FIELD_INITIAL_VALUE + APPENDED_TEXT
    )
    pdf_viewer.element_attribute_is(SECOND_FIELD, "value", SECOND_FIELD_INITIAL_VALUE)

    # Step 5-6: Select all text in the second field and replace it.
    pdf_viewer.triple_click(SECOND_FIELD)
    pdf_viewer.fill_element(SECOND_FIELD, SECOND_FIELD_REPLACEMENT_VALUE)
    pdf_viewer.element_attribute_is(
        SECOND_FIELD, "value", SECOND_FIELD_REPLACEMENT_VALUE
    )
