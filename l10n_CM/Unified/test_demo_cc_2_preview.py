import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.classes.credit_card import CreditCardBase
from modules.page_object import AboutPrefs, CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2886599"


@pytest.fixture()
def add_to_prefs_list(region: str):
    return [("extensions.formautofill.creditCards.supportedCountries", region)]


def test_cc_preview(
    driver: Firefox,
    util: Utilities,
    region: str,
    about_prefs_privacy: AboutPrefs,
    autofill_popup: AutofillPopup,
    credit_card_autofill: CreditCardFill,
    populate_saved_payments: CreditCardBase,
):
    """
    C2886599 -  Verify that hovering over field will preview all eligible fields (except for the CVV field)
    """

    # Open credit card form page
    credit_card_autofill.open()

    # fake data
    credit_card_sample_data = populate_saved_payments

    # Hover over each field and check data preview
    fields_to_test = ["name", "card_number", "expiration_month", "expiration_year"]
    for field in fields_to_test:
        credit_card_autofill.check_autofill_preview_for_field(
            field, credit_card_sample_data
        )

    credit_card_autofill.click_form_field("cvv")
    autofill_popup.ensure_autofill_dropdown_not_visible()
