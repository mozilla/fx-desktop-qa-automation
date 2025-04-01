import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
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
):
    # Create fake data and fill it in
    address_autofill.open()
    autofill_data = address_autofill.fill_and_save(util, autofill_popup)

    # Hover over each field and check data preview
    fields_to_test = ["email", "tel"]
    for field in fields_to_test:
        address_autofill.check_autofill_preview_for_field(
            field, autofill_data, autofill_popup, util
        )
