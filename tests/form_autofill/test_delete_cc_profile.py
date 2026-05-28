import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs
from modules.page_object_autofill import CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122391"


def test_delete_cc_profile(
    driver: Firefox,
    about_prefs_payments: AboutPrefs,
    autofill_popup: AutofillPopup,
    credit_card_autofill: CreditCardFill,
    util: Utilities,
):
    """
    C122391, Ensuring that deleting cc profiles will make it so CC does not show up in the grid

    Arguments:
        about_prefs: AboutPrefs instance
        about_prefs_payments: AboutPrefs instance (privacy category)
        autofill_popup: AutofillPopup instance
        credit_card_autofill: CreditCardFill instance
        util: Utilities instance
    """
    # instantiate objects
    credit_card_autofill.open()

    # scroll to first form field
    credit_card_autofill.scroll_to_form_field()

    # create two profiles
    credit_card_autofill.fill_and_save()
    credit_card_autofill.fill_and_save()

    # navigate to prefs
    about_prefs_payments.open()

    # verify there are 2 profiles at first
    cc_profiles = about_prefs_payments.get_all_saved_cc_profiles()
    about_prefs_payments.wait.until(lambda _: len(cc_profiles) == 2)

    # delete a profile and verify there is only 1 left
    about_prefs_payments.click_on("delete-payment")
    alert = about_prefs_payments.get_alert()
    alert.accept()
    cc_profiles = about_prefs_payments.get_all_saved_cc_profiles()
    about_prefs_payments.wait.until(lambda _: len(cc_profiles) == 1)
