import pytest
from selenium.webdriver import Firefox

from modules.classes.autofill_base import AutofillAddressBase
from modules.page_object_autofill import AddressFill


@pytest.fixture()
def test_case():
    return "2888561"


def test_dropdown_presence_address_field(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    fill_and_save_address: AutofillAddressBase,
):
    """
    C2888561 - Verify that the autofill dropdown is displayed  for the eligible address fields after an address was
    previously saved
    """
    # open address filling url page
    address_autofill.open()

    # scroll to first form field
    address_autofill.scroll_to_form_field()

    fields_to_test = [
        "street_address",
        "address_level_2",
        "address_level_1",
        "postal_code",
        "country_code",
    ]

    address_autofill.verify_field_autofill_dropdown(
        region=region, fields_to_test=fields_to_test
    )
