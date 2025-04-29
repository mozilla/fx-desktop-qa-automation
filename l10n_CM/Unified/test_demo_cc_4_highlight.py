import pytest
from selenium.webdriver import Firefox

from modules.classes.credit_card import CreditCardBase
from modules.page_object import CreditCardFill


@pytest.fixture()
def test_case():
    return "2886601"


def test_cc_yellow_highlight(
    driver: Firefox,
    region: str,
    credit_card_autofill: CreditCardFill,
    fill_and_save_payments: CreditCardBase,
):
    """
    C2886601 - Verify the yellow highlight appears on autofilled fields and make sure csv field is not highlighted
    """
    # Open the credit card fill form and trigger the autofill option
    credit_card_autofill.open()

    # scroll to first form field
    credit_card_autofill.scroll_to_form_field()

    credit_card_autofill.select_first_form_field(autofill=True)

    # Verify that all fields have the yellow highlight, except for the cc-csv field
    credit_card_autofill.verify_field_highlight()
