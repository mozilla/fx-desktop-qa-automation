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
    credit_card_autofill: CreditCardFill,
    region: str,
):
    """
    Verify that saved credit card information is autofilled correctly when selected from the dropdown,
    except for the CVV field.
    Arguments:
        credit_card_autofill: CreditCardFill instance
        autofill_popup: AutofillPopup instance
        util: Utilities instance
        region: region being tested
    """

    # Open credit card form page
    credit_card_autofill.open()

    # Create and save fake credit card data
    credit_card_data = credit_card_autofill.fill_and_save(region)

    # Autocomplete and clear all fields
    credit_card_autofill.clear_and_verify_all_fields(credit_card_data, region=region)

    # Step 5: Click the csc field (cc-csc), ensure autofill popup is not present
    credit_card_autofill.click_on("form-field", labels=["cc-csc"])  # Use single click
    autofill_popup.ensure_autofill_dropdown_not_visible()
