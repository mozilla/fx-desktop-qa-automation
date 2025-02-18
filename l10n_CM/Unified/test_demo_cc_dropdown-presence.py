import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs, CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2886598"


def test_dropdown_presence_credit_card(
    driver: Firefox,
    util: Utilities,
    address_autofill_popup: AutofillPopup,
    about_prefs: AboutPrefs,
    about_prefs_cc_popup: AboutPrefs,
    credit_card_fill_obj: CreditCardFill,
):
    """
    C2886598 - Verify autofill dropdown is displayed only for the eligible fields after a credit card is saved
    """

    # Save a credit card in about:preferences
    about_prefs.open()
    about_prefs.switch_to_saved_payments_popup_iframe()

    credit_card_sample_data = util.fake_credit_card_data()
    about_prefs_cc_popup.click_on(
        "panel-popup-button", labels=["autofill-manage-add-button"]
    )
    about_prefs.fill_cc_panel_information(credit_card_sample_data)

    # Open credit card form page
    credit_card_fill_obj.open()

    # Verify autofill dropdown is displayed only for the eligible fields
    credit_card_fill_obj.verify_autofill_dropdown_all_fields(address_autofill_popup)
