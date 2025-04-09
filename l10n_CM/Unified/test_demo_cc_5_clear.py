import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs, CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2886602"


def test_cc_clear_form(
    driver: Firefox,
    region: str,
    util: Utilities,
    autofill_popup: AutofillPopup,
    about_prefs_privacy: AboutPrefs,
    about_prefs: AboutPrefs,
    credit_card_fill_obj: CreditCardFill,
):
    """
    C2886602 - Verify that clearing the form from any field results in all fields being emptied, regardless of the
    field from which the clear action was triggered.
    """

    # Go to about:preferences#privacy and open Saved Payment Methods
    about_prefs_privacy.open()
    about_prefs_privacy.open_and_switch_to_saved_payments_popup()

    # Save CC information using fake data
    credit_card_sample_data = util.fake_credit_card_data(region)

    # Add a new CC profile
    about_prefs_privacy.click_add_on_dialog_element()
    about_prefs_privacy.add_entry_to_saved_payments(credit_card_sample_data)

    # Open credit card form page, clear form and verify all fields are empty
    credit_card_fill_obj.open()
    for field in credit_card_fill_obj.fields:
        credit_card_fill_obj.clear_and_verify(field, region)
