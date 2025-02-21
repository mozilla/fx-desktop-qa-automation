import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888563"


def autofill_and_verify(address_autofill, address_autofill_popup, field_label, address_autofill_data, region, util):
    # Skip address-level1 (State) selection for DE and FR
    if field_label == "address-level1" and region in ["DE", "FR"]:
        return

    # Double-click a field and choose first element from the autocomplete dropdown
    address_autofill.double_click("form-field", labels=[field_label])
    first_item = address_autofill_popup.get_nth_element(1)
    address_autofill_popup.click_on(first_item)

    # Verify autofill data
    address_autofill.verify_autofill_data(address_autofill_data, region, util)

    # Clear form autofill
    address_autofill.double_click("form-field", labels=[field_label])
    address_autofill_popup.click_clear_form_option()


def test_demo_ad_autofill_address_fields(driver: Firefox, region: str):
    """
    C2888563 - Verify Autofill functionality when selecting an entry from the dropdown for address fields
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

    # List of field labels to be autofilled and verified
    fields_to_test = [
        "street-address",
        "address-level2",
        "address-level1",  # This will be skipped for DE/FR
        "postal-code",
        "country",
        "email",
        "tel"
    ]

    # Loop through each field and perform the autofill test
    for field in fields_to_test:
        autofill_and_verify(address_autofill, address_autofill_popup, field, address_autofill_data, region, util)

