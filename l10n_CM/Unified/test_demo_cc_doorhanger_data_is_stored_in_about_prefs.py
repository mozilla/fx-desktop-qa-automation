import time

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import CreditCardFill
from modules.page_object_prefs import AboutPrefs
from modules.util import Utilities, BrowserActions


@pytest.fixture()
def test_case():
    return "2886597"


def test_cc_data_captured_in_doorhanger_and_stored(driver: Firefox, region: str):
    """
    C2889999 - Verify credit card data is captured in the Capture Doorhanger and stored in about:preferences
    """

    # Instantiate objects
    credit_card_fill_obj = CreditCardFill(driver)
    autofill_popup_obj = AutofillPopup(driver)
    util = Utilities()
    browser_action_obj = BrowserActions(driver)

    # Navigate to page
    credit_card_fill_obj.open()

    # Fill data
    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_fill_obj.fill_credit_card_info(credit_card_sample_data)

    # The "Save credit card?" doorhanger is displayed
    assert autofill_popup_obj.element_visible("doorhanger-save-button"), "Credit card save doorhanger is not visible"

    # Click the "Save" button using click_doorhanger_button
    autofill_popup_obj.click_doorhanger_button("save")

    # Navigate to about:preferences#privacy => "Autofill" section
    about_prefs = AboutPrefs(driver, category="privacy").open()
    iframe = about_prefs.get_save_credit_cards_popup_iframe()
    browser_action_obj.switch_to_iframe_context(iframe)

    time.sleep(2)

    # The credit card saved in step 2 is listed in the "Saved credit cards" modal
    elements = about_prefs.get_elements("saved-credit-cards-values")
    expected_values = [
        credit_card_sample_data.card_number[-4:],  # Only last 4 digits should be stored
        credit_card_sample_data.name,
        f"{credit_card_sample_data.expiration_month}/{credit_card_sample_data.expiration_year[-2:]}"
    ]

    found_credit_card = any(
        all(value in element.text for value in expected_values)
        for element in elements
    )
    assert found_credit_card, "Credit card details were not found in saved credit cards!"