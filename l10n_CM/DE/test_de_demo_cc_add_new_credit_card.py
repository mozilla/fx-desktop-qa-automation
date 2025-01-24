import json
import platform

import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs
from modules.util import BrowserActions, Utilities


@pytest.fixture()
# This needs to be updated when DE is added to TestRail, it's pointing to US test
def test_case():
    return "2886595"


@pytest.mark.xfail(platform.system() == "Linux", reason="Autofill Linux instability")
def test_create_new_cc_profile(driver: Firefox):
    """
    C122389, tests you can create and save a new Credit Card profile
    """
    # instantiate objects
    util = Utilities()
    browser_action_obj = BrowserActions(driver)

    # go to about:preferences#privacy and open Saved Payment Methods
    about_prefs = AboutPrefs(driver, category="privacy").open()
    iframe = about_prefs.get_saved_payments_popup_iframe()
    browser_action_obj.switch_to_iframe_context(iframe)

    # save CC data by using the fake data
    credit_card_sample_data = util.fake_credit_card_data()
    about_prefs_cc_popup = AboutPrefs(driver)

    # add a new CC profile
    about_prefs_cc_popup.get_element(
        "panel-popup-button", labels=["autofill-manage-add-button"]
    ).click()

    about_prefs.fill_cc_panel_information(credit_card_sample_data)

    # get the saved CC data
    cc_profiles = about_prefs_cc_popup.get_all_saved_cc_profiles()
    cc_info_json = json.loads(cc_profiles[0].get_dom_attribute("data-l10n-args"))

    # compare input CC data with saved CC data
    about_prefs.verify_cc_json(cc_info_json, credit_card_sample_data)
