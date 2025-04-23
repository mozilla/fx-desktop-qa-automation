import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.classes.autofill_base import AutofillAddressBase
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
    fill_and_save_address: AutofillAddressBase,
):
    """
    C2888567 - Verify that the autofill dropdown is displayed for the email and phone fields
    after the contact information was previously saved.
    """

    # Open autofill page
    address_autofill.open()

    # scroll to first form field
    address_autofill.scroll_to_form_field()

    fields_to_test = ["email", "telephone"]

    address_autofill.verify_field_autofill_dropdown(
        region=region, fields_to_test=fields_to_test
    )
