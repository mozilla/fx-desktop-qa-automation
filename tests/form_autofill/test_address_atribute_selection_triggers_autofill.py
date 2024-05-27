import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_autofill_popup import AutofillPopup
from modules.util import Utilities
from modules.page_object import AddressFill

countries = ["CA", "US"]


@pytest.mark.parametrize("country_code", countries)
def test_address_atribute_selection(driver: Firefox, country_code: str):
    """
    C122359 - This test verifies that after filling the autofill fields and saving the data, hovering over the first
    item in the dropdown ensures that the actual value matches the expected value.
    """
    # Instantiate objects and open the navigation page
    Navigation(driver).open()
    af = AddressFill(driver).open()
    afp = AutofillPopup(driver)
    util = Utilities()

    # Create fake data, fill in the form, and press submit and save on the doorhanger
    autofill_sample_data = util.fake_autofill_data(country_code)
    af.save_information_basic(autofill_sample_data)
    afp.press_doorhanger_save()

    # Creating new object to prevent stale webelements
    new_af = AddressFill(driver).open()
    new_afp = AutofillPopup(driver)

    # Double-click on the name field to trigger the autocomplete dropdown
    new_af.double_click("form-field", "street-address")

    # Get the first element from the autocomplete dropdown
    first_item = new_afp.get_nth_element("1")
    new_afp.hover_over_element(first_item)

    # Get the primary value (street address) from the first item in the dropdown and assert that the actual value
    # matches the expected value
    actual_value = new_afp.get_primary_value(first_item)
    expected_street_address = autofill_sample_data.street_address
    assert expected_street_address == actual_value, f"Expected {expected_street_address}, but got {actual_value}"
