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
    return "122406"


fields = ["cc-name", "cc-exp-month", "cc-exp-year", "cc-number"]


@pytest.mark.parametrize("field", fields)
def test_update_cc_no_dupe_name(
    driver: Firefox,
    about_prefs_privacy: AboutPrefs,
    autofill_popup: AutofillPopup,
    credit_card_autofill: CreditCardFill,
    util: Utilities,
    field: str,
    region: str,
):
    """
    C122406, ensures that updating the credit card saves the correct information with no dupe profile for the name and expiry dates
    for cvv, must create a new profile

    Arguments:
        about_prefs_privacy: AboutPrefs instance (privacy category)
        autofill_popup: AutofillPopup instance
        credit_card_autofill: CreditCardFill instance
        util: Utilities instance
        field: credit card field being checked
        region: region being tested.
    """
    # navigate to credit card form page
    credit_card_autofill.open()

    # scroll to first form field
    credit_card_autofill.scroll_to_form_field()

    # create and fill fake data
    credit_card_sample_data = credit_card_autofill.fill_and_save()

    # autofill form
    credit_card_autofill.select_autofill_option(field)

    # updating the name of the cc holder
    new_field_value = credit_card_autofill.generate_field_data(
        credit_card_sample_data, field, region
    )
    credit_card_autofill.update_form_data(
        credit_card_sample_data, field, new_field_value, region
    )

    # navigate to settings
    about_prefs_privacy.open()
    about_prefs_privacy.open_and_switch_to_saved_payments_popup()

    # assert no dupe profile is saved
    saved_cc = about_prefs_privacy.get_all_saved_cc_profiles()
    assert len(saved_cc) == 1 if field != "cc-number" else len(saved_cc) == 2

    # preprocessing for validations
    cc_info_json = json.loads(saved_cc[0].get_dom_attribute("data-l10n-args"))
    logging.info(f"The extracted JSON: {cc_info_json}")
    logging.info(f"The extracted cc data: {credit_card_sample_data}")

    # verify the items in the JSON vs the sample data
    about_prefs_privacy.verify_cc_json(cc_info_json, credit_card_sample_data)
