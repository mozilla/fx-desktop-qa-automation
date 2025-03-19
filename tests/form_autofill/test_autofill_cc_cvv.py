import json
import logging

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import CreditCardFill
from modules.page_object_prefs import AboutPrefs
from modules.util import BrowserActions, Utilities


@pytest.fixture()
def test_case():
    return "122399"


def test_autofill_cc_cvv(
    driver: Firefox,
    credit_card_autofill: CreditCardFill,
    autofill_popup: AutofillPopup,
    util: Utilities,
    about_prefs_privacy: AboutPrefs,
):
    """
    C122399, Test form autofill CC CVV number

    Arguments:
        about_prefs_privacy: AboutPrefs instance
        credit_card_autofill: CreditCardFill instance
        autofill_popup: AutofillPopup instance
        util: Utilities instance
    """

    # open credit card autofill page
    credit_card_autofill.open()

    # create fake data, fill it in and press submit and save on the door hanger
    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_autofill.fill_credit_card_info(credit_card_sample_data)
    cvv = credit_card_sample_data.cvv
    autofill_popup.click_doorhanger_button("save")

    # navigate to prefs
    about_prefs_privacy.open()
    about_prefs_privacy.switch_to_saved_payments_popup_iframe()

    # Get the saved CC data (first entry)
    cc_profile = about_prefs_privacy.get_all_saved_cc_profiles()[0]
    cc_info_json = json.loads(cc_profile.get_dom_attribute("data-l10n-args"))

    # Compare input CC data with saved CC data
    about_prefs_privacy.verify_cc_json(cc_info_json, credit_card_sample_data)

    # Click on saved address and edit
    cc_profile.click()
    about_prefs_privacy.click_edit_saved_payment()

    # Verify that CVV number is not saved under CC profile but the rest of the data is saved
    about_prefs_privacy.verify_cc_edit_saved_payments_profile(credit_card_sample_data)
