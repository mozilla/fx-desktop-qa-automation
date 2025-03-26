import json
import logging

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs
from modules.page_object_autofill import CreditCardFill
from modules.util import BrowserActions, Utilities


@pytest.fixture()
def test_case():
    return "122390"


@pytest.fixture()
def hard_quit():
    return True


@pytest.mark.parametrize("num_tabs", range(4))
def test_edit_credit_card_profile(
    driver: Firefox,
    num_tabs: int,
    hard_quit,
    about_prefs_privacy: AboutPrefs,
    util: Utilities,
    credit_card_autofill: CreditCardFill,
    autofill_popup: AutofillPopup,
):
    """
    C122390, ensures that editing a credit card profile in the about:prefs
    has the correct behaviour

    Arguments:
        about_prefs_privacy: AboutPrefs instance (privacy category)
        autofill_popup: AutofillPopup instance
        credit_card_autofill: CreditCardFill instance
        util: Utilities instance
    """

    # fill in cc information
    credit_card_autofill.open()
    credit_card_sample_data_original = util.fake_credit_card_data()
    credit_card_autofill.fill_credit_card_info(credit_card_sample_data_original)
    autofill_popup.click_doorhanger_button("save")

    # navigate to about:prefs and select the saved payment methods
    about_prefs_privacy.open()
    about_prefs_privacy.open_and_switch_to_saved_payments_popup()

    # fetch the saved cc profile and select edit
    saved_profile = about_prefs_privacy.get_element("cc-saved-options")
    info_string = saved_profile.get_attribute("data-l10n-args")
    cc_info_json_original = json.loads(info_string)
    logging.info(f"Extracted Original data: {cc_info_json_original}")
    saved_profile.click()

    # assert that the edit button is clickable
    panel_edit_button = about_prefs_privacy.get_element(
        "panel-popup-button", labels=["autofill-manage-edit-button"]
    )
    about_prefs_privacy.expect(EC.element_to_be_clickable(panel_edit_button))

    # ensure the same year or month is not generated
    credit_card_sample_data_new = util.fake_credit_card_data()
    while (
        len(credit_card_sample_data_new.card_number) < 14
        or credit_card_sample_data_new.card_number[-4:] in info_string
        or credit_card_sample_data_new.expiration_month in info_string
        or credit_card_sample_data_new.expiration_year in info_string
    ):
        credit_card_sample_data_new = util.fake_credit_card_data()

    # create the dict
    tab_num_to_data = {
        0: credit_card_sample_data_new.card_number,
        1: credit_card_sample_data_new.expiration_month,
        2: f"20{credit_card_sample_data_new.expiration_year}",
        3: credit_card_sample_data_new.name,
    }

    tab_num_to_original_data = {
        0: credit_card_sample_data_original.card_number[-4:],
        1: f'"month": "{str(int(credit_card_sample_data_original.expiration_month))}"',
        2: f"20{credit_card_sample_data_original.expiration_year}",
        3: credit_card_sample_data_original.name,
    }

    # modify some values
    panel_edit_button.click()

    about_prefs_privacy.update_cc_field_panel(num_tabs, tab_num_to_data[num_tabs])

    # ensure that the information is updated using a trick with the dialog templates
    about_prefs_privacy.switch_to_default_frame()
    dialog_stack = about_prefs_privacy.get_element("panel-popup-stack")
    about_prefs_privacy.custom_wait(timeout=15).until_not(
        lambda _: len(dialog_stack.find_elements(By.ID, "dialogTemplate")) >= 3,
        message="Timeout waiting for the number of dialogTemplate elements to drop below 3",
    )
    about_prefs_privacy.switch_to_saved_payments_popup_iframe()

    # fetch the edited profile, ensure that the attribute containing the data is new
    about_prefs_privacy.expect_not(
        EC.text_to_be_present_in_element_attribute(
            about_prefs_privacy.get_selector("cc-saved-options"),
            "data-l10n-args",
            tab_num_to_original_data[num_tabs],
        )
    )
    edited_profile = about_prefs_privacy.get_element("cc-saved-options")

    cc_info_json = json.loads(edited_profile.get_attribute("data-l10n-args"))
    logging.info(f"Extracted Edited data: {cc_info_json}")

    # changing the cc number
    logging.info(f"Original Data: {credit_card_sample_data_original.card_number}")
    logging.info(f"New Data: {credit_card_sample_data_new.card_number}")

    if num_tabs == 0:
        credit_card_sample_data_original.card_number = (
            credit_card_sample_data_new.card_number
        )
    elif num_tabs == 1:
        credit_card_sample_data_original.expiration_month = (
            credit_card_sample_data_new.expiration_month
        )
    elif num_tabs == 2:
        credit_card_sample_data_original.expiration_year = (
            credit_card_sample_data_new.expiration_year
        )
    else:
        credit_card_sample_data_original.name = credit_card_sample_data_new.name

    about_prefs_privacy.verify_cc_json(cc_info_json, credit_card_sample_data_original)

    # close the pop-up
    about_prefs_privacy.switch_to_default_frame()
    about_prefs_privacy.click_on("dialog-close-button")
    driver.quit()
