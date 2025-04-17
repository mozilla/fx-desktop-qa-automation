import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.classes.credit_card import CreditCardBase
from modules.page_object import AboutPrefs, CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2886598"


def test_dropdown_presence_credit_card(
    driver: Firefox,
    region: str,
    util: Utilities,
    autofill_popup: AutofillPopup,
    about_prefs_privacy: AboutPrefs,
    credit_card_autofill: CreditCardFill,
    populate_saved_payments: CreditCardBase,
):
    """
    C2886598 - Verify autofill dropdown is displayed only for the eligible fields after a credit card is saved
    """
    # Open credit card form page
    credit_card_autofill.open()

    # Verify autofill dropdown is displayed only for the eligible fields
    credit_card_autofill.verify_field_autofill_dropdown()
