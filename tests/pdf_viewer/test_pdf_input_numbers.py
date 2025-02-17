import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.page_object import GenericPdf

TEST_VALUE = "12345"


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

    Arguments:
        sys_platform: Current System Platform Type
        fillable_pdf_url: pdf file directory path
        downloads_folder: downloads folder path
        delete_files: fixture to remove the files after the test finishes
    """

    pdf = GenericPdf(driver, pdf_url=fillable_pdf_url)

    # Clear the field and enter the test value
    pdf.fill_element("zipcode-field", TEST_VALUE + Keys.TAB)

    # Verify the value is still present
    pdf.element_attribute_contains("zipcode-field", "value", TEST_VALUE)
