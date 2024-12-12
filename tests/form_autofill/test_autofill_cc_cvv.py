import json
import logging
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object import AboutPrefs, CreditCardFill
from modules.util import BrowserActions, Utilities


@pytest.fixture()
def test_case():
    return "122399"


# @pytest.mark.xfail(platform.system() == "Linux", reason="Autofill Linux instability")
def test_autofill_cc_cvv(driver: Firefox, extend_timeout, screenshot):
    """
    C122399, Test form autofill CC CVV number
    """
    # instantiate objects
    credit_card_autofill = CreditCardFill(driver)
    credit_card_autofill.open()
    autofill_popup = AutofillPopup(driver)
    util = Utilities()
    about_prefs_obj = AboutPrefs(driver, category="privacy")
    browser_action_obj = BrowserActions(driver)

    # create fake data, fill it in and press submit and save on the doorhanger
    credit_card_sample_data = util.fake_credit_card_data()
    fields = {
        "cc-name": credit_card_sample_data.name,
        "cc-number": credit_card_sample_data.card_number,
        "cc-exp-month": credit_card_sample_data.expiration_month,
        "cc-exp-year": credit_card_sample_data.expiration_year,
        "cc-csc": credit_card_sample_data.cvv,
    }
    for field, value in fields.items():
        credit_card_autofill.fill(
            "form-field", value, press_enter=False, labels=[field]
        )
    credit_card_autofill.click_on("submit-button", labels=["submit"])
    screenshot("cc_cvv_1")
    cvv = credit_card_sample_data.cvv
    autofill_popup.click_doorhanger_button("save")
    sleep(3)
    screenshot("cc_cvv_2")

    # navigate to prefs

    about_prefs_obj.open()
    iframe = about_prefs_obj.press_button_get_popup_dialog_iframe(
        "Saved payment methods"
    )
    screenshot("cc_cvv_3")
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
