import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs, CreditCardFill
from modules.util import BrowserActions, Utilities


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
    credit_card_fill_obj: CreditCardFill,
):
    """
    C2886599 -  Verify that hovering over field will preview all eligible fields (except for the CVV field)
    """

    # Go to about:preferences#privacy and open Saved Payment Methods
    about_prefs_privacy.open()
    about_prefs_privacy.open_and_switch_to_saved_payments_popup()

    # Save CC information using fake data
    credit_card_sample_data = util.fake_credit_card_data(region)

    # Add a new CC profile
    about_prefs_privacy.click_add_on_dialog_element()
    about_prefs_privacy.add_entry_to_saved_payments(credit_card_sample_data)

    # Open credit card form page
    credit_card_fill_obj.open()

    # Verify the autofill preview
    for field in CreditCardFill.fields:
        credit_card_fill_obj.click_on("form-field", labels=[field])
        autofill_popup.ensure_autofill_dropdown_visible()
        autofill_popup.hover("select-form-option")
        credit_card_fill_obj.verify_autofill_cc_data_on_hover(
            credit_card_sample_data, autofill_popup
        )

    credit_card_fill_obj.click_on("form-field", labels=["cc-csc"])
    autofill_popup.ensure_autofill_dropdown_not_visible()
