import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122405"


def test_autofill_credit_card(
    driver: Firefox,
    util: Utilities,
    credit_card_autofill: CreditCardFill,
    autofill_popup: AutofillPopup,
):
    """
    C122405, tests that after filling autofill and disabling cc info it appears in panel

    Arguments:
        credit_card_autofill: CreditCardFill instance
        autofill_popup: AutofillPopup instance
        util: Utilities instance
    """

    # navigate to credit card autofill page
    credit_card_autofill.open()

    # fill autofill forms with fake cc data and submit
    credit_card_data = credit_card_autofill.fill_and_save()

    # autofill from a given field and verify, repeat for all fields
    credit_card_autofill.autofill_and_clear_all_fields(credit_card_data)
