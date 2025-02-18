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


@pytest.fixture()
def file_name():
    return "i-9.pdf"


def test_pdf_input_numbers(
    driver: Firefox,
    pdf_viewer: GenericPdf,
    downloads_folder: str,
    sys_platform,
    delete_files,
):
    """
    C1017528: Input data in numeric fields

    Arguments:
        sys_platform: Current System Platform Type
        pdf_viewer: instance of GenericPdf with correct path.
        downloads_folder: downloads folder path
        delete_files: fixture to remove the files after the test finishes
    """

    # Clear the field and enter the test value
    pdf_viewer.fill_element("zipcode-field", TEST_VALUE + Keys.TAB)

    # Verify the value is still present
    pdf_viewer.element_attribute_contains("zipcode-field", "value", TEST_VALUE)
