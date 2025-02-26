import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888563"


def test_demo_ad_autofill_address_fields(driver: Firefox, region: str, address_autofill: AddressFill, util: Utilities):
    """
    C2888563 - Verify Autofill functionality when selecting an entry from the dropdown for address fields
    """
    # Instantiate objects
    address_autofill_popup = AutofillPopup(driver)

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
        "country"
    ]

    # Loop through each field and perform the autofill test
    for field in fields_to_test:
        address_autofill.autofill_and_verify(address_autofill_popup, field,
                                             address_autofill_data, util)

