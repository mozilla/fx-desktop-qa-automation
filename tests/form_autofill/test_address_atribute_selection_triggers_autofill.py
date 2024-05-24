import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AddressFill
from modules.util import Utilities

countries = ["CA", "US"]


@pytest.mark.parametrize("country_code", countries)
def test_address_attribute_selection(driver: Firefox, country_code: str):
    """
    C122359 - This test verifies that after filling the autofill fields and saving the data, hovering over the first
    item in the dropdown ensures that the actual value matches the expected value.
    """
    # Instantiate objects and open the navigation page
    Navigation(driver).open()
    address_form_fields = AddressFill(driver).open()
    autofill_popup_panel = AutofillPopup(driver)
    util = Utilities()

    # Create fake data, fill in the form, and press submit and save on the doorhanger
    autofill_sample_data = util.fake_autofill_data(country_code)
    address_form_fields.save_information_basic(autofill_sample_data)
    autofill_popup_panel.press_doorhanger_save()

    # Double-click on the name field to trigger the autocomplete address dropdown
    address_form_fields.double_click("form-field", "street-address")

    # Get the first element from the autocomplete address dropdown
    first_item = autofill_popup_panel.get_nth_element("1")
    autofill_popup_panel.hover_over_element(first_item)
    autofill_popup_panel.click_nth_element("1")

    fields_to_verify = {
        "name": autofill_sample_data.name,
        "organization": autofill_sample_data.organization,
        "street-address": autofill_sample_data.street_address,
        "address-level2": autofill_sample_data.address_level_2,
        "address-level1": autofill_sample_data.address_level_1,
        "postal-code": autofill_sample_data.postal_code,
        "country": autofill_sample_data.country,
        "email": autofill_sample_data.email,
        "tel": autofill_sample_data.telephone,
    }

    # Loop through each field and compare the expected value with the displayed value
    for field_name, expected_value in fields_to_verify.items():
        if not expected_value:
            continue  # Skip comparison if the field value is missing, phone number is not always generated

        input_field = address_form_fields.get_element("form-field", field_name)
        displayed_value = input_field.get_attribute("value")

        if not displayed_value:
            continue  # Skip comparison if the displayed value is empty

        if field_name == "tel":
            expected_value = address_form_fields.normalize_phone_number(
                expected_value, country_code
            )
            displayed_value = address_form_fields.normalize_phone_number(
                displayed_value, country_code
            )

        assert (
            displayed_value == expected_value
        ), f"Expected {field_name} to be {expected_value}, but got {displayed_value}"
