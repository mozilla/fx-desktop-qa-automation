import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object import CreditCardFill


@pytest.fixture()
def test_case():
    return "122405"


def test_autofill_credit_card(
    driver: Firefox,
    credit_card_autofill: CreditCardFill,
    autofill_popup: AutofillPopup,
    region: str,
):
    """
    C122405, tests that after filling autofill and disabling cc info it appears in panel

    Arguments:
        credit_card_autofill: CreditCardFill instance
        autofill_popup: AutofillPopup instance
        region: region being tested
    """

    # navigate to credit card autofill page
    credit_card_autofill.open()

    # scroll to first form field
    credit_card_autofill.scroll_to_form_field()

    # fill autofill forms with fake cc data and submit
    credit_card_data = credit_card_autofill.fill_and_save(region)

    # autofill from a given field and verify, repeat for all fields
    credit_card_autofill.clear_and_verify_all_fields(credit_card_data, region=region)
