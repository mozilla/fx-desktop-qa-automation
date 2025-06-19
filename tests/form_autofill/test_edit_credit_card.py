import json
import logging

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs
from modules.page_object_autofill import CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122390"


@pytest.fixture()
def hard_quit():
    return True


fields = ["expiration_month"]


@pytest.mark.parametrize("field", fields)
def test_edit_credit_card_profile(
    driver: Firefox,
    about_prefs_privacy: AboutPrefs,
    util: Utilities,
    credit_card_autofill: CreditCardFill,
    autofill_popup: AutofillPopup,
    field: str,
    region: str,
    hard_quit,
):
    """
    C122390, ensures that editing a credit card profile in the about:prefs
    has the correct behaviour

    Arguments:
        about_prefs_privacy: AboutPrefs instance (privacy category)
        autofill_popup: AutofillPopup instance
        credit_card_autofill: CreditCardFill instance
        util: Utilities instance
        region: country code in use
        field: cc field being changed
    """

    # Open credit card page
    credit_card_autofill.open()

    # scroll to first form field
    credit_card_autofill.scroll_to_form_field()

    # Fill in fake data
    original_cc_data = credit_card_autofill.fill_and_save()

    # navigate to about:prefs and select the saved payment methods
    about_prefs_privacy.open()
    about_prefs_privacy.open_and_switch_to_saved_payments_popup()

    # fetch the saved cc profile and select edit
    saved_profile = about_prefs_privacy.get_all_saved_cc_profiles()
    saved_profile[0].click()
    about_prefs_privacy.click_edit_on_dialog_element()

    # ensure the same year or month is not generated
    credit_card_sample_data_new = util.fake_credit_card_data(region, original_cc_data)

    # update cc field
    updated_value = getattr(credit_card_sample_data_new, field)
    about_prefs_privacy.update_cc_field_panel(field, updated_value)

    ## get new json object for the updated field
    saved_profile = about_prefs_privacy.get_all_saved_cc_profiles()
    saved_profile[0].click()
    cc_info_json_new = json.loads(saved_profile[0].get_attribute("data-l10n-args"))

    logging.warning(
        f"In Test1: {original_cc_data.expiration_month} -> {cc_info_json_new['month']} and {updated_value}"
    )
    # replace required field value from original cc data
    setattr(original_cc_data, field, updated_value)
    logging.warning(
        f"In Test2: {original_cc_data.expiration_month} -> {cc_info_json_new['month']}"
    )
    # verify that field is changed
    about_prefs_privacy.verify_cc_json(cc_info_json_new, original_cc_data)
