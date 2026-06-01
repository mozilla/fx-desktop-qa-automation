import json
import logging

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object import AboutPrefs, CreditCardFill


@pytest.fixture()
def test_case():
    return "122406"


fields = ["cc-name", "cc-exp-month", "cc-exp-year", "cc-number"]


@pytest.mark.parametrize("field", fields)
def test_update_cc_no_dupe_name(
    driver: Firefox,
    about_prefs_payments: AboutPrefs,
    autofill_popup: AutofillPopup,
    credit_card_autofill: CreditCardFill,
    field: str,
    region: str,
):
    """
    C122406, ensures that updating the credit card saves the correct information with
    no dupe profile for the name and expiry dates. For cvv, must create a new profile.

    Arguments:
        about_prefs_payments: AboutPrefs instance (privacy category)
        autofill_popup: AutofillPopup instance:
        credit_card_autofill: CreditCardFill instance
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
    about_prefs_payments.open()

    # assert no dupe profile is saved
    if field == "cc-number":
        about_prefs_payments.confirm_n_payments(2)
    else:
        about_prefs_payments.confirm_n_payments(1)

    # preprocessing for validations
    cc_info_json = about_prefs_payments.get_data_from_saved_payment(0)
    logging.info(f"The extracted JSON: {cc_info_json}")
    logging.info(f"The extracted cc data: {credit_card_sample_data}")

    # verify the items in the JSON vs the sample data
    about_prefs_payments.verify_cc_json(cc_info_json, credit_card_sample_data)
