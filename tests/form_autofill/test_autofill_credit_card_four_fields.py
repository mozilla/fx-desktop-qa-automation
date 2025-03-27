import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122404"


def test_autofill_four_fields(
    driver: Firefox,
    autofill_popup: AutofillPopup,
    credit_card_autofill: CreditCardFill,
    util: Utilities,
):
    """
    C122404, tests that the form fields are filled corrected after saving a profile.

    Arguments:
        autofill_popup: AutofillPopup instance
        credit_card_autofill: CreditCardFill instance
        util: Utilities instance
    """
    # navigate to credit card autofill page
    credit_card_autofill.open()

    # fill autofill forms with fake cc data and submit
    credit_card_data = credit_card_autofill.fill_and_save(util, autofill_popup)

    # select autofill dropdown option
    credit_card_autofill.select_autofill_option(autofill_popup, "cc-name")

    # verify cc data is correct
    credit_card_autofill.verify_credit_card_form_data(credit_card_data)
