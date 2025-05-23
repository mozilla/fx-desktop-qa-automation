import pytest
from selenium.webdriver import Firefox

from modules.classes.autofill_base import AutofillAddressBase
from modules.page_object_autofill import AddressFill


@pytest.fixture()
def test_case():
    return "2888556"


def test_dropdown_presence_name_organization(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    fill_and_save_address: AutofillAddressBase,
):
    """
    C2888556 - Verify that the autofill dropdown is displayed  for the name and organization fields after an address was
    previously saved
    """
    # open address filling url page
    address_autofill.open()

    # scroll to first form field
    address_autofill.scroll_to_form_field()

    # Verify that the name and organization fields have the autofill dropdown present
    fields_to_test = ["name", "given_name", "family_name", "organization"]

    address_autofill.verify_field_autofill_dropdown(
        region=region, fields_to_test=fields_to_test
    )
