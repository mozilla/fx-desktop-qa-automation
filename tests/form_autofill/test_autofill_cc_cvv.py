import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object import AboutPrefs, CreditCardFill


@pytest.fixture()
def test_case():
    return "122399"


def test_autofill_cc_cvv(
    driver: Firefox,
    credit_card_autofill: CreditCardFill,
    autofill_popup: AutofillPopup,
    about_prefs_payments: AboutPrefs,
):
    """
    C122399, Test form autofill CC CVV number

    Arguments:
        about_prefs_payments: AboutPrefs instance (payments category)
        credit_card_autofill: CreditCardFill instance
        autofill_popup: AutofillPopup instance
    """

    # Open credit card autofill page
    credit_card_autofill.open()

    # scroll to first form field
    credit_card_autofill.scroll_to_form_field()

    # Create fake data, fill it in and press submit and save on the door hanger
    credit_card_sample_data = credit_card_autofill.fill_and_save()

    # Navigate to prefs
    about_prefs_payments.open()

    # Get the saved CC data (first entry)
    cc_info_json = about_prefs_payments.get_data_from_saved_payment()

    # Compare input CC data with saved CC data
    about_prefs_payments.verify_cc_json(cc_info_json, credit_card_sample_data)

    # Click on saved address and edit
    about_prefs_payments.click_on("edit-payment")

    # Verify that CVV number is not saved under CC profile but the rest of the data is saved
    about_prefs_payments.verify_cc_edit_saved_payments_profile(credit_card_sample_data)
