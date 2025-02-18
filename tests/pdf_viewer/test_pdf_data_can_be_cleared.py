import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.page_object import GenericPdf

TEST_NAME = "John Doe"


@pytest.fixture()
def test_case():
    return "1017495"


@pytest.fixture()
def delete_files_regex_string():
    return r"i-9.*\.pdf"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return "i-9.pdf"


@pytest.mark.ci
def test_pdf_data_can_be_cleared(
    driver: Firefox,
    pdf_viewer: GenericPdf,
    downloads_folder: str,
    sys_platform,
    delete_files,
):
    """
    C1017495 :Check if data can be cleared

    Arguments:
        sys_platform: Current System Platform Type
        pdf_viewer: instance of GenericPdf with correct path.
        downloads_folder: downloads folder path
        delete_files: fixture to remove the files after the test finishes
    """
    # Step 1: Click and type inside the text field for the name section

    pdf_viewer.fill("first-name-field", TEST_NAME)
    pdf_viewer.element_attribute_contains("first-name-field", "value", TEST_NAME)

    # Step 2: Click over any checkbox and assert the status is updated

    checkbox = pdf_viewer.select_and_return_checkbox("first-checkbox")
    pdf_viewer.element_selected("first-checkbox")

    # Step 3: Select an option from a dropdown and verify the selection

    dropdown_option = pdf_viewer.select_and_return_dropdown_option(
        "state-dropdown-field", By.XPATH, "//option[@value='CA']"
    )
    pdf_viewer.expect(lambda _: dropdown_option.is_displayed())

    # Step 4: Delete the text added in step 1 and ensure the input field is empty
    pdf_viewer.get_element("first-name-field").clear()
    pdf_viewer.expect(
        lambda _: not pdf_viewer.get_element("first-name-field").get_attribute("value")
    )

    # Step 5: Click the checkbox from step 2 again and ensure it returns to its previous state
    checkbox.click()
    pdf_viewer.expect(lambda _: not checkbox.is_selected())

    # Step 6: Clear the state selection and ensure the field is empty
    default_option = pdf_viewer.select_and_return_dropdown_option(
        "state-dropdown-field", By.XPATH, "//option[@value=' ']"
    )
    default_option.click()
    pdf_viewer.expect(lambda _: default_option.is_selected())
