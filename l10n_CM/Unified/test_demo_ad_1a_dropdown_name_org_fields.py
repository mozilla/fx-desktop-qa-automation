import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.classes.autofill_base import AutofillAddressBase
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888556"


def test_dropdown_presence_name_organization(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    util: Utilities,
    autofill_popup: AutofillPopup,
    fill_and_save_address: AutofillAddressBase,
):
    """
    C2888556 - Verify that the autofill dropdown is displayed  for the name and organization fields after an address was
    previously saved
    """
    # open address filling url page
    address_autofill.open()

    # Verify that the name and organization fields have the autofill dropdown present
    fields_to_test = ["name", "given_name", "family_name", "organization"]

    address_autofill.verify_field_autofill_dropdown(
        region=region, fields_to_test=fields_to_test
    )
