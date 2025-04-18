import json

import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2886595"


def test_create_new_cc_profile(
    driver: Firefox, region: str, util: Utilities, about_prefs_privacy: AboutPrefs
):
    """
    C2886595 - Tests you can create and save a new Credit Card profile
    """

    # Go to about:preferences#privacy and open Saved Payment Methods
    about_prefs_privacy.open()
    about_prefs_privacy.open_and_switch_to_saved_payments_popup()

    # Save CC information using fake data
    credit_card_sample_data = util.fake_credit_card_data(region)

    # Add a new CC profile
    about_prefs_privacy.click_add_on_dialog_element()
    about_prefs_privacy.add_entry_to_saved_payments(credit_card_sample_data)

    # Get the saved CC data
    cc_profiles = about_prefs_privacy.get_all_saved_cc_profiles()
    assert cc_profiles, "No saved cc profiles found"

    cc_info_json = json.loads(cc_profiles[0].get_dom_attribute("data-l10n-args"))

    # Compare input CC data with saved CC data
    about_prefs_privacy.verify_cc_json(cc_info_json, credit_card_sample_data)
