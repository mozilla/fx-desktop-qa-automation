import pytest
from selenium.webdriver.common.keys import Keys

from modules.page_object import GenericPdf
from modules.util import Utilities

PDF_FILE_NAME = "i-9.pdf"


@pytest.fixture()
def test_case():
    return "1017527"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


def test_pdf_copy_paste_functionality(pdf_viewer: GenericPdf):
    """
    1017527: Verify that text can be pasted in a PDF form text field
    """
    util = Utilities()
    random_text = util.generate_random_text("word")

    # Step 1: PDF form with text fields is opened by the pdf_viewer fixture.
    pdf_viewer.element_visible("first-name-field")

    # Step 2: Copy a random text
    pdf_viewer.fill("first-name-field", random_text, press_enter=False)
    pdf_viewer.triple_click("first-name-field")
    pdf_viewer.copy()

    # Step 3: Click inside the text field for the name section.
    pdf_viewer.get_element("first-name-field").clear()
    pdf_viewer.element_attribute_is("first-name-field", "value", "")
    pdf_viewer.click_on("first-name-field")

    # Step 4: Paste the previously copied text.
    pdf_viewer.paste()
    pdf_viewer.element_attribute_is("first-name-field", "value", random_text)

    # Step 5: Click or tab out of the input field and verify the text remains.
    pdf_viewer.get_element("first-name-field").send_keys(Keys.TAB)
    pdf_viewer.element_attribute_is("first-name-field", "value", random_text)
