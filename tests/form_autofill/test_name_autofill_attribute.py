import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122356"


def test_name_attribute_selection(
    driver: Firefox,
    address_autofill: AddressFill,
    autofill_popup: AutofillPopup,
    util: Utilities,
    region: str,
):
    """
    C122356 - This test verifies that after filling the autofill fields and saving the data, hovering over the first
    item in the dropdown ensures that the actual value matches the expected value.
    Verifies name attribute.

    Arguments:
        address_autofill: AddressFill instance
        autofill_popup: AutofillPopup instance
        util: Utilities instance
        region: country code in use
    """
    # open the navigation page
    address_autofill.open()

    # scroll to first form field
    address_autofill.scroll_to_form_field()

    # Create fake data, fill in the form, and press submit and save on the doorhanger
    autofill_sample_data = address_autofill.fill_and_save(region)

    # Double-click on the name field to trigger the autocomplete dropdown
    address_autofill.double_click("form-field", labels=["name"])

    # Get the first element from the autocomplete dropdown
    first_item = autofill_popup.get_nth_element(1)
    actual_value = autofill_popup.hover(first_item).get_primary_value(first_item)

    # Get the primary value (street address) from the first item in the dropdown and assert that the actual value
    # matches the expected value
    expected_name = autofill_sample_data.name
    assert (
        expected_name == actual_value
    ), f"Expected {expected_name}, but got {actual_value}"
