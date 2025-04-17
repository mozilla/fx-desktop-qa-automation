import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.classes.autofill_base import AutofillAddressBase
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888560"


def test_demo_ad_clear_name_org(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    util: Utilities,
    autofill_popup: AutofillPopup,
    fill_and_save_address: AutofillAddressBase,
):
    """
    C2888560 - Verify clear functionality after selecting an entry from name/org fields
    """
    # Create fake data and fill it in
    address_autofill.open()

    # List of field labels to be autofilled and verified
    fields_to_test = ["name", "given_name", "family_name", "organization"]

    # Loop through each field and perform the autofill test
    for field in fields_to_test:
        address_autofill.clear_and_verify(field, region=region)
