import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs, CreditCardFill
from modules.util import BrowserActions, Utilities


@pytest.fixture()
def test_case():
    return "2886601"


def test_cc_yellow_highlight(driver: Firefox):
    """
    C2886601 - Verify the yellow highlight appears on autofilled fields and make sure csv field is not highlighted
    """

    # Initialize objects
    util = Utilities()
    about_prefs = AboutPrefs(driver, category="privacy")
    about_prefs_cc_popup = AboutPrefs(driver)
    browser_action_obj = BrowserActions(driver)
    credit_card_fill_obj = CreditCardFill(driver)
    autofill_popup = AutofillPopup(driver)

    # Save a credit card in about:preferences
    about_prefs.open()
    iframe = about_prefs.get_saved_payments_popup_iframe()
    browser_action_obj.switch_to_iframe_context(iframe)
    credit_card_sample_data = util.fake_credit_card_data()
    about_prefs_cc_popup.click_on(
        "panel-popup-button", labels=["autofill-manage-add-button"]
    )
    about_prefs.fill_cc_panel_information(credit_card_sample_data)

    # Open the credit card fill form and trigger the autofill option
    credit_card_fill_obj.open()
    credit_card_fill_obj.click_on("form-field", labels=["cc-name"])
    autofill_popup.click_autofill_form_option()

    # Verify that all fields have the yellow highlight, except for the cc-csv field
    credit_card_fill_obj.verify_field_yellow_highlights()
