import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.classes.autofill_base import AutofillAddressBase
from modules.page_object_autofill import AddressFill
from modules.page_object_prefs import AboutPrefs
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888568"


def test_hover_email_and_phone_autofill_preview(
    driver: Firefox,
    region: str,
    about_prefs_privacy: AboutPrefs,
    address_autofill: AddressFill,
    autofill_popup: AutofillPopup,
    util: Utilities,
    fill_and_save_address: AutofillAddressBase,
):
    # Create fake data
    address_autofill.open()

    # created fake data
    autofill_data = fill_and_save_address

    # Hover over each field and check data preview
    fields_to_test = ["email", "telephone"]
    for field in fields_to_test:
        address_autofill.check_autofill_preview_for_field(field, autofill_data, region)
