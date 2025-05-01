import json

import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122389"


def test_create_new_cc_profile(
    driver: Firefox,
    about_prefs_privacy: AboutPrefs,
    about_prefs: AboutPrefs,
    util: Utilities,
):
    """
    C122389, tests you can create and save a new Credit Card profile

    Arguments:
        about_prefs_privacy: AboutPrefs instance (privacy category)
        about_prefs: AboutPrefs instance
        util: Utilities instance
    """
    # go to about:preferences#privacy and open Saved Payment Methods
    about_prefs_privacy.open()
    about_prefs_privacy.open_and_switch_to_saved_payments_popup()

    # save CC data by using the fake data
    credit_card_sample_data = util.fake_credit_card_data()

    # add a new CC profile
    about_prefs_privacy.click_add_on_dialog_element()
    about_prefs_privacy.add_entry_to_saved_payments(credit_card_sample_data)

    about_prefs_privacy.open_and_switch_to_saved_payments_popup()

    # get the saved CC data
    cc_profiles = about_prefs_privacy.get_all_saved_cc_profiles()
    cc_info_json = json.loads(cc_profiles[0].get_dom_attribute("data-l10n-args"))

    # compare input CC data with saved CC data
    about_prefs.verify_cc_json(cc_info_json, credit_card_sample_data)
