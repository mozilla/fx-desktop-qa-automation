import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs, CreditCardFill
from modules.util import Utilities



@pytest.fixture()
def test_case():
    return "2886600"


def test_cc_autofill_from_dropdown(
    driver: Firefox,
    util: Utilities,
    autofill_popup: AutofillPopup,
    credit_card_fill_obj: CreditCardFill,

):
    """
    Verify that saved credit card information is autofilled correctly when selected from the dropdown,
    except for the CVV field.
    """

    # Open credit card form page
    credit_card_fill_obj.open()

    # Create and save fake credit card data
    credit_card_data = util.fake_credit_card_data()
    credit_card_fill_obj.fill_credit_card_info(credit_card_data)
    autofill_popup.click_doorhanger_button("save")

    # Autocomplete and clear all fields
    credit_card_fill_obj.autofill_and_clear_all_fields(autofill_popup, credit_card_data)

    # Step 5: Click the csc field (cc-csc), ensure autofill popup is not present
    credit_card_fill_obj.click_on("form-field", labels=["cc-csc"])  # Use single click
    autofill_popup.ensure_autofill_dropdown_not_visible()