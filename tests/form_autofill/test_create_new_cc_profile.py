import json

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import AboutPrefsCcPopup, Navigation
from modules.page_object import AboutPrefs
from modules.util import BrowserActions, Utilities

# Browser regions in which the Credit cards can be saved in
countries = ["CA", "US"]


@pytest.mark.parametrize("country_code", countries)
def test_create_new_cc_profile(driver: Firefox, country_code: str):
    """
    C122389, tests you can create and save a new Credit Card profile
    """
    # instantiate objects
    nav = Navigation(driver)
    util = Utilities()
    nav.open()
    browser_action_obj = BrowserActions(driver)

    # go to about:preferences#privacy and open Saved Payment Methods
    about_prefs = AboutPrefs(driver, category="privacy").open()
    iframe = about_prefs.get_saved_payments_popup_iframe()
    browser_action_obj.switch_to_iframe_context(iframe)

    # save CC data by using the fake data
    credit_card_sample_data = util.fake_credit_card_data()
    about_prefs_cc_popup = AboutPrefsCcPopup(driver, iframe)

    # add a new CC profile
    about_prefs_cc_popup.get_element(
        "cc-popup-button", labels=["autofill-manage-add-button"]
    ).click()
    about_prefs.actions.send_keys(credit_card_sample_data.card_number).perform()
    about_prefs.actions.send_keys(Keys.TAB).perform()
    about_prefs.actions.send_keys(credit_card_sample_data.expiration_month).perform()
    about_prefs.actions.send_keys(Keys.TAB).perform()
    about_prefs.actions.send_keys(
        f"20{credit_card_sample_data.expiration_year}"
    ).perform()
    about_prefs.actions.send_keys(Keys.TAB).perform()
    about_prefs.actions.send_keys(credit_card_sample_data.name).perform()
    about_prefs.actions.send_keys(Keys.TAB).perform()
    about_prefs.actions.send_keys(Keys.TAB).perform()
    about_prefs.actions.send_keys(Keys.ENTER).perform()

    # get the saved CC data
    cc_profiles = about_prefs_cc_popup.get_all_saved_cc_profiles()
    cc_info_json = json.loads(cc_profiles[0].get_dom_attribute("data-l10n-args"))

    # compare input CC data with saved CC data
    about_prefs.verify_cc_json(cc_info_json, credit_card_sample_data)
