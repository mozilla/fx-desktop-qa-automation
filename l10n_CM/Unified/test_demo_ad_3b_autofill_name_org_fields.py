import pytest
from selenium.webdriver import Firefox

from modules.classes.autofill_base import AutofillAddressBase
from modules.page_object_autofill import AddressFill


@pytest.fixture()
def test_case():
    return "2888558"


def test_demo_ad_autofill_name_org(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    fill_and_save_address: AutofillAddressBase,
):
    """
    C2888558 - Verify Autofill functionality when selecting an entry from the dropdown for name/org fields
    """
    # Create fake data
    address_autofill.open()

    # scroll to first form field
    address_autofill.scroll_to_form_field()

    # created fake data
    autofill_data = fill_and_save_address

    # List of field labels to be autofilled and verified
    fields_to_test = ["name", "given_name", "family_name", "organization"]

    # Loop through each field and perform the autofill test
    for field in fields_to_test:
        address_autofill.clear_and_verify(field, autofill_data, region=region)
