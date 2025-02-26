import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888570"


def test_address_yellow_highlight_address_fields(driver: Firefox, region: str):
    """
    C2888570 - Verify the yellow highlight appears on autofilled fields for the email and phone fields.
    """

    # Instantiate objects
    address_autofill = AddressFill(driver)
    address_autofill_popup = AutofillPopup(driver)
    util = Utilities()

    # Create fake data and fill it in
    address_autofill.open()
    address_autofill_data = util.fake_autofill_data(region)
    address_autofill.save_information_basic(address_autofill_data)

    # Click the "Save" button
    address_autofill_popup.click_doorhanger_button("save")

    # Double click inside email field and select a saved address entry from the dropdown
    address_autofill.double_click("form-field", labels=["email"])

    # Click on the first element from the autocomplete dropdown
    first_item = address_autofill_popup.get_nth_element(1)
    address_autofill_popup.click_on(first_item)

    # Verify the email and phone fields are highlighted
    address_autofill.verify_field_yellow_highlights(
        fields_to_test=["email", "tel"], expected_highlighted_fields=["email", "tel"]
    )
