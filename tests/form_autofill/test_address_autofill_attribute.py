import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122359"


def test_address_attribute_selection(
    driver: Firefox,
    address_autofill: AddressFill,
    autofill_popup: AutofillPopup,
    util: Utilities,
    region: str,
):
    """
    C122359 - This test verifies that after filling the autofill fields and saving the data, hovering over the first
    item in the dropdown ensures that the actual value matches the expected value.

    Arguments:
        address_autofill: AddressFill instance
        autofill_popup: AutofillPopup instance
        util: Utilities instance
        region: country code in use
    """
    # open the navigation page
    address_autofill.open()

    # Create fake data, fill in the form, and press submit and save on the doorhanger
    autofill_sample_data = util.fake_autofill_data(region)
    address_autofill.save_information_basic(autofill_sample_data)
    autofill_popup.click_doorhanger_button("save")

    # Double-click on the name field to trigger the autocomplete dropdown
    address_autofill.double_click("form-field", labels=["street-address"])

    # Get the first element from the autocomplete dropdown
    first_item = autofill_popup.get_nth_element(1)
    actual_value = autofill_popup.hover(first_item).get_primary_value(first_item)

    # Get the primary value (street address) from the first item in the dropdown and assert that the actual value
    # matches the expected value
    expected_street_address = autofill_sample_data.street_address
    assert expected_street_address == actual_value, (
        f"Expected {expected_street_address}, but got {actual_value}"
    )
