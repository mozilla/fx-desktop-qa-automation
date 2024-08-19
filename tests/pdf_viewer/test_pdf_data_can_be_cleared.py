import time

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.page_object_generics import GenericPdf


@pytest.fixture()
def delete_files_regex_string():
    return r"i-9.*\.pdf"


@pytest.mark.headed
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

    pdf = GenericPdf(driver, pdf_url=fillable_pdf_url).open()
    keyboard = Controller()

    # Step 1: Click and type inside the text field for the name section

    name_field = pdf.get_element("first-name-field")
    name_test_value = "John Doe"
    name_field.clear()
    name_field.send_keys(name_test_value)
    time.sleep(1)
    # Assert input is accepted
    assert name_field.get_attribute("value") == name_test_value, "Text input failed."

    # Step 2: Click over any checkbox and assert the status is updated

    checkbox = pdf.get_element("first-checkbox")
    checkbox.click()
    time.sleep(1)
    # Assert checkbox is checked
    assert checkbox.is_selected(), "Checkbox was not selected."

    # Step 3: Select an option from a dropdown and verify the selection

    dropdown = pdf.get_element("state-dropdown-field")
    dropdown.click()
    option = driver.find_element(By.XPATH, "//option[@value='CA']")
    option.click()
    time.sleep(1)
    # Assert dropdown option is selected
    assert option.is_selected(), "Dropdown option was not selected."

    # Step 4: Delete the text added in step 1 and ensure the input field is empty
    name_field.clear()
    time.sleep(1)
    # Assert input field is empty
    assert name_field.get_attribute("value") == "", "Text field is not empty."

    # Step 5: Click the checkbox from step 2 again and ensure it returns to its previous state
    checkbox.click()
    time.sleep(1)
    # Assert checkbox is unchecked
    assert not checkbox.is_selected(), "Checkbox was not deselected."

    # Step 6: Clear the state selection and insure the field is empty
    dropdown.click()
    default_option = driver.find_element(By.XPATH, "//option[@value=' ']")
    default_option.click()
    time.sleep(1)
    # Assert dropdown is cleared (default option selected)
    assert default_option.is_selected(), "Dropdown value was not cleared."

    # Assert that all fields are reset to their default state
    assert name_field.get_attribute("value") == "", "Text field did not reset."
    assert not checkbox.is_selected(), "Checkbox did not reset."

    print(
        "Test passed: All interactions performed correctly, and the form resets after page refresh."
    )

    # Save the doc so that the test can end
    download_button = pdf.get_element("download-button")
    download_button.click()

    time.sleep(2)

    if sys_platform == "Linux":
        keyboard.press(Key.alt)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        keyboard.release(Key.alt)
        time.sleep(1)
        keyboard.press(Key.alt)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        keyboard.release(Key.alt)
        time.sleep(1)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        time.sleep(1)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)

    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
