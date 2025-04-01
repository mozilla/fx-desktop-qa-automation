import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888565"


def test_demo_ad_clear_address_fields(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    util: Utilities,
    autofill_popup: AutofillPopup,
):
    """
    C2888565 - Verify clear functionality after selecting an entry from address fields
    """
    # Create fake data and fill it in
    address_autofill.open()
    address_autofill_data = address_autofill.fill_and_save(util, autofill_popup)

    # List of field labels to be autofilled and verified
    fields_to_test = [
        "street-address",
        "address-level2",
        "address-level1",  # This will be skipped for DE/FR
        "postal-code",
        "country",
    ]

    # Loop through each field and perform the autofill test
    for field in fields_to_test:
        address_autofill.clear_and_verify(autofill_popup, field, address_autofill_data)
