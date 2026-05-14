import pytest
from selenium.webdriver.common.keys import Keys

from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"
NUMERIC_TEXT = "1907"


@pytest.fixture()
def test_case():
    return "1017529"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


def test_pdf_text_can_be_pasted_in_numeric_field(pdf_viewer: GenericPdf):
    """
    C1017529: Verify that numeric text can be pasted in a PDF form numeric field
    """
    # Step 1: PDF form with numeric fields is opened by the pdf_viewer fixture.
    pdf_viewer.element_visible("zipcode-field")

    # Step 2: Copy a numeric text.
    pdf_viewer.fill("zipcode-field", NUMERIC_TEXT, press_enter=False)
    pdf_viewer.triple_click("zipcode-field")
    pdf_viewer.copy()

    # Step 3: Click inside the numeric field.
    pdf_viewer.get_element("zipcode-field").clear()
    pdf_viewer.element_attribute_is("zipcode-field", "value", "")
    pdf_viewer.click_on("zipcode-field")

    # Step 4: Paste the previously copied numeric text.
    pdf_viewer.paste()
    pdf_viewer.element_attribute_is("zipcode-field", "value", NUMERIC_TEXT)

    # Step 5: Click or tab out of the input field and verify the numeric text remains.
    pdf_viewer.fill_element("zipcode-field", Keys.TAB)
    pdf_viewer.element_attribute_is("zipcode-field", "value", NUMERIC_TEXT)
