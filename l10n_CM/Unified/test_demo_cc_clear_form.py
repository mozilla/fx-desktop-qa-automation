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
    util: Utilities,
    address_autofill_popup: AutofillPopup,
    about_prefs: AboutPrefs,
    about_prefs_cc_popup: AboutPrefs,
    credit_card_fill_obj: CreditCardFill,
):
    """
    C2886602 - Verify that clearing the form from any field results in all fields being emptied, regardless of the
    field from which the clear action was triggered.
    """

    # Save a credit card in about:preferences
    about_prefs.open()
    about_prefs.switch_to_saved_payments_popup_iframe()

    credit_card_sample_data = util.fake_credit_card_data()
    about_prefs_cc_popup.click_on(
        "panel-popup-button", labels=["autofill-manage-add-button"]
    )
    about_prefs.fill_cc_panel_information(credit_card_sample_data)

    # Open credit card form page, clear form and verify all fields are empty
    credit_card_fill_obj.open()
    credit_card_fill_obj.verify_clear_form_all_fields(address_autofill_popup)
