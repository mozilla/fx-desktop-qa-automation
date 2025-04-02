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
    address_autofill.fill_and_save(util, autofill_popup, region)

    fields_to_test = [
        "street-address",
        "address-level2",
        "address-level1",
        "postal-code",
        "country",
    ]

    address_autofill.verify_autofill_dropdown_addresses(
        autofill_popup=autofill_popup, fields_to_test=fields_to_test, region=region
    )
