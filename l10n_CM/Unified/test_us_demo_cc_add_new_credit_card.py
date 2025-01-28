import json

import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutConfig, AboutPrefs
from modules.util import BrowserActions, Utilities

regions = ["US", "CA", "DE", "FR"]


@pytest.fixture()
def test_case():
    return "2886595"


@pytest.mark.parametrize("region", regions)
def test_create_new_cc_profile(driver: Firefox, region: str):
    """
    C2886595 - tests you can create and save a new Credit Card profile
    """

    # Instantiate objects
    util = Utilities()
    browser_action_obj = BrowserActions(driver)
    about_prefs = AboutPrefs(driver, category="privacy")
    about_prefs_cc_popup = AboutPrefs(driver)
    about_config = AboutConfig(driver)

    # Change pref value of region
    about_config.change_pref_value("browser.search.region", region)

    # Go to about:preferences#privacy and open Saved Payment Methods
    about_prefs.open()
    iframe = about_prefs.get_saved_payments_popup_iframe()
    browser_action_obj.switch_to_iframe_context(iframe)

    # Save CC information using fake data
    credit_card_sample_data = util.fake_credit_card_data()

    # Add a new CC profile
    about_prefs_cc_popup.element_clickable(
        "panel-popup-button", labels=["autofill-manage-add-button"]
    )
    about_prefs_cc_popup.click_on(
        "panel-popup-button", labels=["autofill-manage-add-button"]
    )
    about_prefs.fill_cc_panel_information(credit_card_sample_data)

    # Get the saved CC data
    cc_profiles = about_prefs_cc_popup.get_all_saved_cc_profiles()
    cc_info_json = json.loads(cc_profiles[0].get_dom_attribute("data-l10n-args"))

    # Compare input CC data with saved CC data
    about_prefs.verify_cc_json(cc_info_json, credit_card_sample_data)
