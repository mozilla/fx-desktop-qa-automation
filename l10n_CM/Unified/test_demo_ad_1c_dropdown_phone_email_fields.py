import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888567"


def test_dropdown_presence_email_phone_field(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    util: Utilities,
    autofill_popup: AutofillPopup,
):
    """
    C2888567 - Verify that the autofill dropdown is displayed for the email and phone fields
    after the contact information was previously saved.
    """

    # Open autofill page and fill fake data
    address_autofill.open()
    address_autofill.fill_and_save(util, autofill_popup, region)

    fields_to_test = ["email", "tel"]

    address_autofill.verify_autofill_dropdown_addresses(
        autofill_popup=autofill_popup, fields_to_test=fields_to_test, region=region
    )
