import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.page_object import GenericPdf


@pytest.fixture()
def test_case():
    return "1017528"


@pytest.fixture()
def delete_files_regex_string():
    return r"i-9.*\.pdf"


@pytest.fixture()
def hard_quit():
    return True


def test_pdf_input_numbers(
    driver: Firefox,
    fillable_pdf_url: str,
    downloads_folder: str,
    sys_platform,
    delete_files,
):
    """
    C1017528: Input data in numeric fields
    """

    pdf = GenericPdf(driver, pdf_url=fillable_pdf_url)
    pdf.open()
    numeric_field = pdf.get_element("zipcode-field")

    # Test value to input in the field
    test_value = "12345"

    # Clear the field and enter the test value
    numeric_field.send_keys(test_value + Keys.TAB)

    # Verify the value is still present
    pdf.element_attribute_contains("zipcode-field", "value", test_value)
