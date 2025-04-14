import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888561"


def test_dropdown_presence_address_field(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    util: Utilities,
    autofill_popup: AutofillPopup,
):
    """
    C2888561 - Verify that the autofill dropdown is displayed  for the eligible address fields after an address was
    previously saved
    """

    # Create fake data and fill it in
    address_autofill.open()
    address_autofill.fill_and_save(region)

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
