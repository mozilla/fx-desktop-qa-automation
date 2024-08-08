import time
import pytest
from selenium.webdriver import Firefox
from modules.page_object_generics import GenericPdf


@pytest.mark.headed
def test_pdf_input_numbers(driver: Firefox, fillable_pdf_url: str):
    """
    C1017528: Input data in numeric fields
    """
    from pynput.keyboard import Controller, Key

    pdf = GenericPdf(driver, pdf_url=fillable_pdf_url).open()
    keyboard = Controller()

    numeric_field = pdf.get_element("zipcode-field")

    # Test value to input in the field
    test_value = "12345"

    # Clear the field and enter the test value
    numeric_field.clear()
    numeric_field.send_keys(test_value)

    # Press Tab to move to the next field (if applicable)
    keyboard.release(Key.tab)

    # Allow time for the field to update
    time.sleep(2)

    # Verify the value is still present
    value = numeric_field.get_attribute("value")
    assert value == test_value, f"Expected value {test_value}, but got {value}."

    print(
        "Test passed: Numeric field has been filled correctly and the value persists."
    )
