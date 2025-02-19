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

    # get the text from the row and split by the comma, striping any leading or trailing whitespace on the way.
    elements = [x.strip() for x in about_prefs.get_element("saved-credit-cards-values").text.split(',')]

    # Validate stored values match expected values
    assert elements[0].endswith(credit_card_sample_data.card_number[-4:]), \
        f"Expected last 4 digits '{credit_card_sample_data.card_number[-4:]}' but got '{elements[0]}'"

    assert elements[1] == credit_card_sample_data.name, \
        f"Expected name '{credit_card_sample_data.name}' but got '{elements[1]}'"

    expected_expiry = f"Expires on {int(credit_card_sample_data.expiration_month)}/20{credit_card_sample_data.expiration_year}"
    assert elements[2] == expected_expiry, \
        f"Expected expiration '{expected_expiry}' but got '{elements[2]}'"
