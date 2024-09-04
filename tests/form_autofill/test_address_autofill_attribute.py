import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122359"


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

    # Double-click on the name field to trigger the autocomplete dropdown
    address_form_fields.double_click("form-field", labels=["street-address"])

    # Get the first element from the autocomplete dropdown
    first_item = autofill_popup_panel.get_nth_element(1)
    actual_value = autofill_popup_panel.hover(first_item).get_primary_value(first_item)

    # Get the primary value (street address) from the first item in the dropdown and assert that the actual value
    # matches the expected value
    expected_street_address = autofill_sample_data.street_address
    assert (
        expected_street_address == actual_value
    ), f"Expected {expected_street_address}, but got {actual_value}"
