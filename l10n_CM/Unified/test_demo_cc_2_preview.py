import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs, CreditCardFill
from modules.util import BrowserActions, Utilities


@pytest.fixture()
def test_case():
    return "2886599"


@pytest.fixture()
def add_to_prefs_list(region: str):
    return [("extensions.formautofill.creditCards.supportedCountries", region)]


def test_cc_preview(
    driver: Firefox,
    util: Utilities,
    about_prefs_privacy: AboutPrefs,
    autofill_popup: AutofillPopup,
    credit_card_fill_obj: CreditCardFill,
):
    """
    C2886599 -  Verify that hovering over field will preview all eligible fields (except for the CVV field)
    """

    browser_action_obj = BrowserActions(driver)

    # Save a credit card in about:preferences
    about_prefs_privacy.open()
    iframe = about_prefs_privacy.get_saved_payments_popup_iframe()
    browser_action_obj.switch_to_iframe_context(iframe)

    # Generate fake CC data & add it
    credit_card_sample_data = util.fake_credit_card_data()
    about_prefs_privacy.click_on(
        "panel-popup-button", labels=["autofill-manage-add-button"]
    )
    about_prefs_privacy.fill_and_save_cc_panel_information(credit_card_sample_data)

    # Open the credit card fill form
    credit_card_fill_obj.open()

    # Verify the autofill preview
    for field in CreditCardFill.fields:
        credit_card_fill_obj.click_on("form-field", labels=[field])
        autofill_popup.ensure_autofill_dropdown_visible()
        autofill_popup.hover("select-form-option")
        credit_card_fill_obj.verify_autofill_cc_data_on_hover(
            credit_card_sample_data, autofill_popup
        )

    credit_card_fill_obj.click_on("form-field", labels=["cc-csc"])
    autofill_popup.ensure_autofill_dropdown_not_visible()
