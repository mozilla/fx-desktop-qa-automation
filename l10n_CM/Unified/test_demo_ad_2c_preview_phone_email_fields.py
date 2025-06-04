import pytest
from selenium.webdriver import Firefox

from modules.classes.autofill_base import AutofillAddressBase
from modules.page_object_autofill import AddressFill
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "2888568"


def test_hover_email_and_phone_autofill_preview(
    driver: Firefox,
    region: str,
    about_prefs_privacy: AboutPrefs,
    address_autofill: AddressFill,
    fill_and_save_address: AutofillAddressBase,
):
    """
    C2888568: Verify that hovering over phone/email fields will preview all fields
    """
    # Create fake data
    address_autofill.open()

    # scroll to first form field
    address_autofill.scroll_to_form_field()

    # created fake data
    autofill_data = fill_and_save_address

    # Hover over each field and check data preview
    fields_to_test = ["email", "telephone"]
    for field in fields_to_test:
        address_autofill.check_autofill_preview_for_field(field, autofill_data, region)
