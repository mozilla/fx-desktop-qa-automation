import pytest
from selenium.webdriver import Firefox

from modules.classes.autofill_base import AutofillAddressBase
from modules.page_object_autofill import AddressFill


@pytest.fixture()
def test_case():
    return "2888563"


def test_demo_ad_autofill_address_fields(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    fill_and_save_address: AutofillAddressBase,
):
    """
    C2888563 - Verify Autofill functionality when selecting an entry from the dropdown for address fields
    """
    # Create fake data
    address_autofill.open()

    # scroll to first form field
    address_autofill.scroll_to_form_field()

    # created fake data
    autofill_data = fill_and_save_address

    # List of field labels to be autofilled and verified
    fields_to_test = [
        "street_address",
        "address_level_2",
        "address_level_1",
        "postal_code",
        "country_code",
    ]
    # Loop through each field and perform the autofill test
    for field in fields_to_test:
        address_autofill.clear_and_verify(field, autofill_data, region=region)
