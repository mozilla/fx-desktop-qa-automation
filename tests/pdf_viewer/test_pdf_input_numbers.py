import time

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


@pytest.mark.headed
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

    from pynput.keyboard import Controller, Key

    pdf = GenericPdf(driver, pdf_url=fillable_pdf_url)
    pdf.open()
    keyboard = Controller()
    numeric_field = pdf.get_element("zipcode-field")

    # Test value to input in the field
    test_value = "12345"

    # Clear the field and enter the test value
    numeric_field.send_keys(test_value + Keys.TAB)

    # Verify the value is still present
    pdf.element_attribute_contains("zipcode-field", "value", test_value)

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
