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
    about_prefs_payments: AboutPrefs,
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
    about_prefs_payments.open()

    # save CC data by using the fake data
    credit_card_sample_data = util.fake_credit_card_data()

    # add a new CC profile
    about_prefs_payments.add_entry_to_saved_payments(credit_card_sample_data)

    # get the saved CC data
    cc_info_json = about_prefs_payments.get_data_from_saved_payment()

    # compare input CC data with saved CC data
    about_prefs.verify_cc_json(cc_info_json, credit_card_sample_data)
