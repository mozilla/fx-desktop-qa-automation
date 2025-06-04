import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.classes.credit_card import CreditCardBase
from modules.page_object import CreditCardFill


@pytest.fixture()
def test_case():
    return "3056985"


def test_cc_autofill_from_dropdown(
    driver: Firefox,
    autofill_popup: AutofillPopup,
    credit_card_autofill: CreditCardFill,
    fill_and_save_payments: CreditCardBase,
    region: str,
):
    """
    C3056985 - Verify that saved credit card information is autofilled correctly when selected from the dropdown,
    except for the CVV field.
    Arguments:
        credit_card_autofill: CreditCardFill instance
        autofill_popup: AutofillPopup instance
        region: region being tested
        fill_and_save_payments: fixture to populate data before test.
    """

    # Open credit card form page
    credit_card_autofill.open()

    # scroll to first form field
    credit_card_autofill.scroll_to_form_field()

    # Create and save fake credit card data
    credit_card_data = fill_and_save_payments

    # Autocomplete and clear all fields
    credit_card_autofill.clear_and_verify_all_fields(credit_card_data, region=region)

    # Step 5: Click the csc field (cc-csc), ensure autofill popup is not present
    credit_card_autofill.verify_no_dropdown_on_field_interaction(
        "cvv"
    )  # Use single click
