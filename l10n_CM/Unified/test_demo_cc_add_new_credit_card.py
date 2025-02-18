import json

import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2886595"


def test_create_new_cc_profile(
    driver: Firefox,
    region: str,
    util: Utilities,
    about_prefs: AboutPrefs,
    about_prefs_cc_popup: AboutPrefs,
):
    """
    C2886595 - Tests you can create and save a new Credit Card profile
    """

    # Go to about:preferences#privacy and open Saved Payment Methods
    about_prefs.open()
    about_prefs.switch_to_saved_payments_popup_iframe()

    # Save CC information using fake data
    credit_card_sample_data = util.fake_credit_card_data()

    # Add a new CC profile
    about_prefs_cc_popup.click_on(
        "panel-popup-button", labels=["autofill-manage-add-button"]
    )
    about_prefs.fill_cc_panel_information(credit_card_sample_data)

    # Get the saved CC data
    cc_profiles = about_prefs_cc_popup.get_all_saved_cc_profiles()
    cc_info_json = json.loads(cc_profiles[0].get_dom_attribute("data-l10n-args"))

    # Compare input CC data with saved CC data
    about_prefs.verify_cc_json(cc_info_json, credit_card_sample_data)
