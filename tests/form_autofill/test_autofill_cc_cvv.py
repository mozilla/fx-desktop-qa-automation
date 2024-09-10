import json
import logging

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.browser_object_navigation import Navigation
from modules.page_object_about_prefs import AboutPrefs
from modules.page_object_autofill_credit_card import CreditCardFill
from modules.util import BrowserActions, Utilities


@pytest.fixture()
def test_case():
    return "122399"


@pytest.mark.unstable
def test_autofill_cc_cvv(driver: Firefox):
    """
    C122399, Test form autofill CC CVV number
    """
    # instantiate objects
    Navigation(driver).open()
    credit_card_autofill = CreditCardFill(driver).open()
    autofill_popup = AutofillPopup(driver)
    util = Utilities()
    about_prefs_obj = AboutPrefs(driver, category="privacy")
    browser_action_obj = BrowserActions(driver)

    # create fake data, fill it in and press submit and save on the doorhanger
    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_autofill.fill_credit_card_info(credit_card_sample_data)
    cvv = credit_card_sample_data.cvv
    autofill_popup.click_doorhanger_button("save")

    # navigate to prefs

    about_prefs_obj.open()
    iframe = about_prefs_obj.press_button_get_popup_dialog_iframe(
        "Saved payment methods"
    )
    browser_action_obj.switch_to_iframe_context(iframe)

    # Select the saved cc
    saved_profile = about_prefs_obj.get_element("cc-saved-options")
    info_string = saved_profile.get_attribute("data-l10n-args")
    cc_info_json_original = json.loads(info_string)
    logging.info(f"Extracted Original data: {cc_info_json_original}")
    saved_profile.click()

    # Click on edit
    about_prefs_obj.get_element(
        "panel-popup-button", labels=["autofill-manage-edit-button"]
    ).click()

    # Verify that CVV number is not saved under CC profile
    element = about_prefs_obj.get_element("cc-saved-options", multiple=True)
    cvv_not_displayed = not any(cvv in element.text for element in element)
    assert cvv_not_displayed, "CVV is displayed."
