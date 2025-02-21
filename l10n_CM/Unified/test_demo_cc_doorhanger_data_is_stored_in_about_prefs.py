import time

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import CreditCardFill
from modules.page_object_prefs import AboutPrefs
from modules.util import BrowserActions, Utilities


@pytest.fixture()
def test_case():
    return "2886597"


def test_demo_cc_data_captured_in_doorhanger_and_stored(driver: Firefox, region: str):
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
    assert autofill_popup_obj.element_visible("doorhanger-save-button"), (
        "Credit card save doorhanger is not visible"
    )

    # Verify Credit Card Doorhanger Data
    doorhanger_text = autofill_popup_obj.get_cc_doorhanger_data("cc-doorhanger-data")
    assert credit_card_sample_data.card_number[-4:] in doorhanger_text, (
        f"Expected last 4 digits '{credit_card_sample_data.card_number[-4:]}' but not found."
    )
    assert credit_card_sample_data.name in doorhanger_text, (
        f"Expected name '{credit_card_sample_data.name}' but not found."
    )
    assert credit_card_sample_data.cvv not in doorhanger_text, (
        f"CVV '{credit_card_sample_data.cvv}' should not be saved, but found in doorhanger."
    )

    # Click the "Save" button using click_doorhanger_button
    autofill_popup_obj.click_doorhanger_button("save")

    # Navigate to about:preferences#privacy => "Autofill" section
    about_prefs = AboutPrefs(driver, category="privacy").open()
    iframe = about_prefs.get_saved_payments_popup_iframe()
    browser_action_obj.switch_to_iframe_context(iframe)

    # Get stored values
    elements = [
        x.strip()
        for x in about_prefs.get_element("saved-credit-cards-values").text.split(",")
    ]

    # Validate stored values match expected values
    assert elements[0].endswith(credit_card_sample_data.card_number[-4:]), (
        f"Expected last 4 digits '{credit_card_sample_data.card_number[-4:]}' but got '{elements[0]}'"
    )
    assert elements[1] == credit_card_sample_data.name, (
        f"Expected name '{credit_card_sample_data.name}' but got '{elements[1]}'"
    )
    assert credit_card_sample_data.cvv not in elements, (
        f"CVV '{credit_card_sample_data.cvv}' should not be saved, but found in stored values."
    )
