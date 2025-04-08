import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888563"


def test_demo_ad_autofill_address_fields(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    util: Utilities,
    autofill_popup: AutofillPopup,
):
    """
    C2888563 - Verify Autofill functionality when selecting an entry from the dropdown for address fields
    """
    # Create fake data and fill it in
    address_autofill.open()
    address_autofill_data = address_autofill.fill_and_save(region)

    # List of field labels to be autofilled and verified
    fields_to_test = [
        "address-level1",  # This will be skipped for DE/FR
        "address-level2",
        "street-address",
        "postal-code",
        "country",
    ]

    # Loop through each field and perform the autofill test
    for field in fields_to_test:
        address_autofill.autofill_and_verify(field, address_autofill_data)
