import json
import logging

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs
from modules.page_object_autofill import CreditCardFill
from modules.util import BrowserActions, Utilities


@pytest.fixture()
def test_case():
    return "122406"


fields = ["cc-name", "cc-exp-month", "cc-exp-year"]


@pytest.mark.parametrize("field", fields)
def test_update_cc_no_dupe_name(driver: Firefox, field: str):
    """
    C122406, ensures that updating the credit card saves the correct information with no dupe profile for the name and expiry dates
    """
    nav = Navigation(driver)
    util = Utilities()

    nav.open()
    credit_card_fill_obj = CreditCardFill(driver).open()
    autofill_popup_obj = AutofillPopup(driver)
    browser_action_obj = BrowserActions(driver)

    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_fill_obj.fill_credit_card_info(credit_card_sample_data)
    autofill_popup_obj.click_doorhanger_button("save")
    credit_card_fill_obj.press_autofill_panel(autofill_popup_obj)

    # updating the name of the cc holder
    if field == "cc-name":
        credit_card_fill_obj.update_cc_name(
            util, credit_card_sample_data, autofill_popup_obj
        )
    elif field == "cc-exp-month":
        credit_card_fill_obj.update_cc_exp_month(
            util, credit_card_sample_data, autofill_popup_obj
        )
    else:
        credit_card_fill_obj.update_cc_exp_year(
            util, credit_card_sample_data, autofill_popup_obj
        )

    # navigate to settings
    about_prefs = AboutPrefs(driver, category="privacy").open()
    iframe = about_prefs.get_saved_payments_popup_iframe()
    browser_action_obj.switch_to_iframe_context(iframe)

    # assert no dupe profile is saved
    element = about_prefs.get_element("cc-saved-options", multiple=True)
    assert len(element) == 1

    # preprocessing for validations
    cc_info_json = json.loads(element[0].get_dom_attribute("data-l10n-args"))
    browser_action_obj.switch_to_content_context()
    logging.info(f"The extracted JSON: {cc_info_json}")
    logging.info(f"The extracted cc data: {credit_card_sample_data}")

    # verify the items in the JSON vs the sample data
    about_prefs.verify_cc_json(cc_info_json, credit_card_sample_data)


def test_update_cc_number_new_profile(driver: Firefox):
    """
    C122406, continuation ensures that updating the credit card number saves a new card instead of updating the new one
    """
    nav = Navigation(driver)
    util = Utilities()

    nav.open()
    credit_card_fill_obj = CreditCardFill(driver).open()
    autofill_popup_obj = AutofillPopup(driver)
    browser_action_obj = BrowserActions(driver)

    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_fill_obj.fill_credit_card_info(credit_card_sample_data)
    autofill_popup_obj.click_doorhanger_button("save")
    credit_card_fill_obj.press_autofill_panel(autofill_popup_obj)

    # updating the card number of the cc holder
    new_sample_data = util.fake_credit_card_data()
    credit_card_fill_obj.update_credit_card_information(
        autofill_popup_obj,
        "cc-number",
        new_sample_data.card_number,
        save_card=True,
    )

    # navigate to settings
    about_prefs = AboutPrefs(driver, category="privacy").open()
    iframe = about_prefs.get_saved_payments_popup_iframe()
    browser_action_obj.switch_to_iframe_context(iframe)

    # assert new profile is saved
    element = about_prefs.get_element("cc-saved-options", multiple=True)
    assert len(element) == 2
