import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.classes.autofill_base import AutofillAddressBase
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888569"


def test_demo_ad_autofill_phone_email(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    autofill_popup: AutofillPopup,
    util: Utilities,
    fill_and_save_address: AutofillAddressBase,
):
    """
    C2888569 - Verify Autofill functionality when selecting an entry from the dropdown for tele/email fields
    """
    # Create fake data
    address_autofill.open()

    # scroll to first form field
    address_autofill.scroll_to_form_field()

    # created fake data
    autofill_data = fill_and_save_address

    # List of field labels to be autofilled and verified
    fields_to_test = ["email", "telephone"]

    # Loop through each field and perform the autofill test
    for field in fields_to_test:
        address_autofill.clear_and_verify(field, autofill_data, region=region)
