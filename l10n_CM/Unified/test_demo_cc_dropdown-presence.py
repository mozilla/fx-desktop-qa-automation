import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs, CreditCardFill
from modules.util import BrowserActions, Utilities


@pytest.fixture()
def test_case():
    return "2886598"


def test_dropdown_presence_credit_card(driver: Firefox):
    """
    C2886598 - Verify autofill dropdown is displayed only for the eligible fields after a credit card is saved
    """

    # Initialize objects
    util = Utilities()
    about_prefs = AboutPrefs(driver, category="privacy")
    about_prefs_cc_popup = AboutPrefs(driver)
    browser_action_obj = BrowserActions(driver)
    credit_card_fill_obj = CreditCardFill(driver)
    autofill_popup_obj = AutofillPopup(driver)

    # Save a credit card in about:preferences
    about_prefs.open()
    iframe = about_prefs.get_saved_payments_popup_iframe()
    browser_action_obj.switch_to_iframe_context(iframe)
    credit_card_sample_data = util.fake_credit_card_data()
    about_prefs_cc_popup.click_on(
        "panel-popup-button", labels=["autofill-manage-add-button"]
    )
    about_prefs.fill_cc_panel_information(credit_card_sample_data)

    # Open credit card form page
    credit_card_fill_obj.open()

    # Verify autofill dropdown is displayed only for the eligible fields
    credit_card_fill_obj.verify_autofill_dropdown_all_fields(autofill_popup_obj)
