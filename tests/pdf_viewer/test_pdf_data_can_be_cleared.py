import logging
import time
from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation
from modules.page_object import GenericPdf


@pytest.fixture()
def test_case():
    return "1017495"


@pytest.fixture()
def delete_files_regex_string():
    return r"i-9.*\.pdf"


@pytest.fixture()
def hard_quit():
    return True


def test_pdf_data_can_be_cleared(
    driver: Firefox,
    fillable_pdf_url: str,
    downloads_folder: str,
    sys_platform,
    delete_files,
):
    """
    C1017495 :Check if data can be cleared
    """

    from pynput.keyboard import Controller, Key

    pdf = GenericPdf(driver, pdf_url=fillable_pdf_url)
    pdf.open()
    keyboard = Controller()

    # Step 1: Click and type inside the text field for the name section

    name_test_value = "John Doe"
    pdf.fill("first-name-field", name_test_value)
    pdf.element_attribute_contains("first-name-field", "value", name_test_value)

    # Step 2: Click over any checkbox and assert the status is updated

    checkbox = pdf.get_element("first-checkbox")
    checkbox.click()
    pdf.element_selected("first-checkbox")

    # Step 3: Select an option from a dropdown and verify the selection

    dropdown = pdf.get_element("state-dropdown-field")
    dropdown.click()
    option = driver.find_element(By.XPATH, "//option[@value='CA']")
    option.click()
    pdf.expect(lambda _: option.is_displayed())

    # Step 4: Delete the text added in step 1 and ensure the input field is empty
    pdf.get_element("first-name-field").clear()
    pdf.get_element("first-name-field").clear()
    pdf.expect(lambda _: not pdf.get_element("first-name-field").get_attribute("value"))

    # Step 5: Click the checkbox from step 2 again and ensure it returns to its previous state
    checkbox.click()
    pdf.expect(lambda _: not checkbox.is_selected())

    # Step 6: Clear the state selection and ensure the field is empty
    dropdown.click()
    default_option = driver.find_element(By.XPATH, "//option[@value=' ']")
    default_option.click()
    pdf.expect(lambda _: default_option.is_selected())

    # Assert that all fields are reset to their default state
    assert (
        pdf.get_element("first-name-field").get_attribute("value") == ""
    ), "Text field did not reset."
    assert not checkbox.is_selected(), "Checkbox did not reset."

    # Save the doc so that the test can end
    nav = Navigation(driver)
    download_button = pdf.get_element("download-button")
    download_button.click()
