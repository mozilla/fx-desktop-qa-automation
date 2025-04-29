import pytest
from selenium.webdriver import Firefox

from modules.classes.autofill_base import AutofillAddressBase
from modules.page_object_autofill import AddressFill


@pytest.fixture()
def test_case():
    return "2888565"


def test_demo_ad_clear_address_fields(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    fill_and_save_address: AutofillAddressBase,
):
    """
    C2888565 - Verify clear functionality after selecting an entry from address fields
    """
    # Create fake data and fill it in
    address_autofill.open()

    # scroll to first form field
    address_autofill.scroll_to_form_field()

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
        address_autofill.clear_and_verify(field, region=region)
