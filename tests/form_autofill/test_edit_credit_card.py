import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object import AboutPrefs, CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122390"


@pytest.fixture()
def hard_quit():
    return True


fields = ["expiration_year", "name", "expiration_month", "card_number"]


@pytest.mark.parametrize("field", fields)
def test_edit_credit_card_profile(
    driver: Firefox,
    about_prefs_payments: AboutPrefs,
    util: Utilities,
    credit_card_autofill: CreditCardFill,
    autofill_popup: AutofillPopup,
    field: str,
    region: str,
):
    """
    C122390, ensures that editing a credit card profile in the about:prefs
    has the correct behaviour

    Arguments:
        about_prefs_payments: AboutPrefs instance (privacy category)
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
    about_prefs_payments.open()

    # fetch the saved cc profile and select edit
    about_prefs_payments.edit_payment()

    # ensure the same year or month is not generated
    credit_card_sample_data_new = util.fake_credit_card_data(region, original_cc_data)

    # update cc field
    updated_value = getattr(credit_card_sample_data_new, field)
    about_prefs_payments.update_cc_field_panel(field, updated_value)
    about_prefs_payments.open()  # reopen payment prefs to reset

    # get new json object for the updated field

    cc_info_json_new = about_prefs_payments.get_data_from_saved_payment()
    # replace required field value from original cc data
    setattr(original_cc_data, field, updated_value)

    # verify that field is changed
    about_prefs_payments.verify_cc_json(cc_info_json_new, original_cc_data)
