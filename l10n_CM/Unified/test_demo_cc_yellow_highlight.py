import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs, CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2886601"


def test_cc_yellow_highlight(
    driver: Firefox,
    region: str,
    util: Utilities,
    about_prefs_privacy: AboutPrefs,
    about_prefs: AboutPrefs,
    credit_card_fill_obj: CreditCardFill,
    autofill_popup: AutofillPopup,
):
    """
    C2886601 - Verify the yellow highlight appears on autofilled fields and make sure csv field is not highlighted
    """

    # Save a credit card in about:preferences
    about_prefs_privacy.open()
    about_prefs_privacy.open_and_switch_to_saved_payments_popup()
    credit_card_sample_data = util.fake_credit_card_data(region)
    about_prefs.click_on("panel-popup-button", labels=["autofill-manage-add-button"])
    about_prefs.fill_cc_panel_information(credit_card_sample_data)

    # Open the credit card fill form and trigger the autofill option
    credit_card_fill_obj.open()
    credit_card_fill_obj.click_on("form-field", labels=["cc-name"])
    autofill_popup.click_autofill_form_option()

    # Verify that all fields have the yellow highlight, except for the cc-csv field
    credit_card_fill_obj.verify_field_yellow_highlights()
