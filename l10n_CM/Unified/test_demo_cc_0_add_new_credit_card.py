import json

import pytest
from selenium.webdriver import Firefox

from modules.classes.credit_card import CreditCardBase
from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "3056980"


def test_create_new_cc_profile(
    driver: Firefox,
    region: str,
    about_prefs_privacy: AboutPrefs,
    populate_saved_payments: CreditCardBase,
):
    """
    C3056980 - Tests you can create and save a new Credit Card profile
    """
    # get sample data
    credit_card_sample_data = populate_saved_payments

    # open about_prefs saved payments profiles
    about_prefs_privacy.open_and_switch_to_saved_payments_popup()

    # Get the saved CC data
    cc_profiles = about_prefs_privacy.get_all_saved_cc_profiles()
    assert cc_profiles, "No saved cc profiles found"

    cc_info_json = json.loads(cc_profiles[0].get_dom_attribute("data-l10n-args"))

    # Compare input CC data with saved CC data
    about_prefs_privacy.verify_cc_json(cc_info_json, credit_card_sample_data)
