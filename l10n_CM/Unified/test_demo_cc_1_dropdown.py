import pytest
from selenium.webdriver import Firefox

from modules.classes.credit_card import CreditCardBase
from modules.page_object import CreditCardFill


@pytest.fixture()
def test_case():
    return "2886598"


def test_dropdown_presence_credit_card(
    driver: Firefox,
    region: str,
    credit_card_autofill: CreditCardFill,
    fill_and_save_payments: CreditCardBase,
):
    """
    C2886598 - Verify autofill dropdown is displayed only for the eligible fields after a credit card is saved
    """
    # Open credit card form page
    credit_card_autofill.open()

    # scroll to first form field
    credit_card_autofill.scroll_to_form_field()

    # Verify autofill dropdown is displayed only for the eligible fields
    credit_card_autofill.verify_field_autofill_dropdown()
