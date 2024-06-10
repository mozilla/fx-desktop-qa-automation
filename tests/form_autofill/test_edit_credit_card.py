import json
import logging
from time import sleep

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import CreditCardPopup, Navigation
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs
from modules.page_object_autofill_credit_card import CreditCardFill
from modules.util import BrowserActions, Utilities

# tabs = [i for i in range(4)]
tabs = [1]


@pytest.mark.parametrize("num_tabs", tabs)
def test_edit_credit_card_profile(driver: Firefox, num_tabs: int):
    """
    C122390, ensures that editing a credit card profile in the about:prefs
    has the correct behaviour
    """
    # instantiate objects
    nav = Navigation(driver)
    about_prefs_obj = AboutPrefs(driver, category="privacy")
    util = Utilities()
    browser_action_obj = BrowserActions(driver)
    credit_card_fill_obj = CreditCardFill(driver).open()
    autofill_popup_obj = AutofillPopup(driver)

    # fill in cc information
    nav.open()
    credit_card_fill_obj.open()
    credit_card_sample_data_original = util.fake_credit_card_data()
    credit_card_fill_obj.fill_credit_card_info(credit_card_sample_data_original)
    autofill_popup_obj.press_doorhanger_save()

    # navigate to about:prefs and select the saved payment methods
    about_prefs_obj.open()
    iframe = about_prefs_obj.press_button_get_popup_dialog_iframe(
        "Saved payment methods"
    )
    browser_action_obj.switch_to_iframe_context(iframe)

    # fetch the saved cc profile and select edit
    saved_profile = about_prefs_obj.get_element("cc-saved-options")
    info_string = saved_profile.get_attribute("data-l10n-args")
    cc_info_json_original = json.loads(info_string)
    logging.info(f"Extracted Original data: {cc_info_json_original}")
    saved_profile.click()

    # assert that the edit button is clickable
    panel_edit_button = about_prefs_obj.get_element(
        "panel-popup-button", labels=["autofill-manage-edit-button"]
    )
    about_prefs_obj.expect(EC.element_to_be_clickable(panel_edit_button))

    # ensure the same year or month is not generated
    credit_card_sample_data_new = util.fake_credit_card_data()
    while len(credit_card_sample_data_new.card_number or credit_card_sample_data_new.card_number[-4:] in info_string) < 14:
        credit_card_sample_data_new = util.fake_credit_card_data()

    # modify some values
    panel_edit_button.click()
    about_prefs_obj.update_cc_field_panel(0, credit_card_sample_data_new.card_number)

    logging.info(f"New data: {credit_card_sample_data_new.expiration_month}")
    # fetch the edited profile, ensure that the attribute containing the data is new
    about_prefs_obj.expect_not(
        EC.text_to_be_present_in_element_attribute(
            about_prefs_obj.get_selector("cc-saved-options"),
            "data-l10n-args",
            credit_card_sample_data_original.card_number[-4:],
        )
    )
    edited_profile = about_prefs_obj.get_element("cc-saved-options")
    cc_info_json = json.loads(edited_profile.get_attribute("data-l10n-args"))
    logging.info(f"Extracted Edited data: {cc_info_json}")

    # changing the cc number
    logging.info(f"Original Data: {credit_card_sample_data_original.card_number}")
    logging.info(f"New Data: {credit_card_sample_data_new.card_number}")

    credit_card_sample_data_original.card_number = credit_card_sample_data_new.card_number

    about_prefs_obj.verify_cc_json(cc_info_json, credit_card_sample_data_original)
