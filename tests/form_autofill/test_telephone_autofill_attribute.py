import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122361"


@pytest.mark.ci
def test_telephone_attribute_autofill(
    driver: Firefox,
    address_autofill: AddressFill,
    autofill_popup: AutofillPopup,
    util: Utilities,
    region: str,
):
    """
    C122356 - This test verifies that after filling the autofill fields and saving the data, hovering over the first
    item in the dropdown ensures that the actual value matches the expected value.
    Verifies Telephone

    Arguments:
        address_autofill: AddressFill instance
        autofill_popup: AutofillPopup instance
        util: Utilities instance
        region: country code in use
    """
    # open the navigation page
    address_autofill.open()

    # Create fake data, fill in the form, and press submit and save on the doorhanger
    autofill_sample_data = address_autofill.fill_and_save(util, autofill_popup, region)

    # Double-click on the name field to trigger the autocomplete dropdown
    address_autofill.double_click("form-field", labels=["tel"])

    # Get the first element from the autocomplete dropdown
    first_item = autofill_popup.get_nth_element(1)
    actual_value = autofill_popup.hover(first_item).get_primary_value(first_item)

    # normalize phone number
    actual_value = util.normalize_phone_number(actual_value)

    # Get the primary value (telephone) from the first item in the dropdown and assert that the actual value
    # matches the expected value
    expected_telephone = util.normalize_phone_number(autofill_sample_data.telephone)
    assert expected_telephone == actual_value, (
        f"Expected {expected_telephone}, but got {actual_value}"
    )
