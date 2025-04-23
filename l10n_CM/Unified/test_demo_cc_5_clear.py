import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.classes.credit_card import CreditCardBase
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
    credit_card_autofill: CreditCardFill,
    fill_and_save_payments: CreditCardBase,
):
    """
    C2886602 - Verify that clearing the form from any field results in all fields being emptied, regardless of the
    field from which the clear action was triggered.
    """

    # Open credit card form page, clear form and verify all fields are empty
    credit_card_autofill.open()

    # scroll to first form field
    credit_card_autofill.scroll_to_form_field()

    fields = [x for x in credit_card_autofill.field_mapping.keys() if x != "cvv"]
    for field in fields:
        credit_card_autofill.clear_and_verify(field, region=region)
