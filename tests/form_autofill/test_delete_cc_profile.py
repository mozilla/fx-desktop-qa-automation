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
    about_prefs: AboutPrefs,
    about_prefs_privacy: AboutPrefs,
    autofill_popup: AutofillPopup,
    credit_card_autofill: CreditCardFill,
    util: Utilities,
):
    """
    C122391, Ensuring that deleting cc profiles will make it so CC does not show up in the grid

    Arguments:
        about_prefs: AboutPrefs instance
        about_prefs_privacy: AboutPrefs instance (privacy category)
        autofill_popup: AutofillPopup instance
        credit_card_autofill: CreditCardFill instance
        util: Utilities instance
    """
    # instantiate objects
    credit_card_autofill.open()

    # create two profiles
    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_autofill.fill_credit_card_info(credit_card_sample_data)
    autofill_popup.click_doorhanger_button("save")

    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_autofill.fill_credit_card_info(credit_card_sample_data)
    autofill_popup.click_doorhanger_button("save")

    # navigate to prefs
    about_prefs_privacy.open()
    about_prefs_privacy.open_and_switch_to_saved_payments_popup()

    # verify there are 2 profiles at first
    cc_profiles = about_prefs.get_all_saved_cc_profiles()
    assert len(cc_profiles) == 2

    # delete a profile and verify there is only 1 left
    cc_profiles[0].click()
    about_prefs.click_popup_panel_button("autofill-manage-remove-button")
    cc_profiles = about_prefs.get_all_saved_cc_profiles()
    assert len(cc_profiles) == 1
