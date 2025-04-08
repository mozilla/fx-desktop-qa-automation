import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object_autofill import CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122401"


def test_form_autofill_suggestions(
    driver: Firefox,
    autofill_popup: AutofillPopup,
    credit_card_autofill: CreditCardFill,
    util: Utilities,
):
    """
    C122401, checks that the corresponding autofill suggestion autofills the fields correctly

    Arguments:
        autofill_popup: AutofillPopup instance
        credit_card_autofill: CreditCardFill instance
        util: Utilities instance
    """
    credit_card_autofill.open()
    # create fake data, two profiles
    sample_data = [credit_card_autofill.fill_and_save() for _ in range(2)]
    # reverse data list to match form options
    sample_data.reverse()

    # press the corresponding option (according to the parameter)
    credit_card_autofill.click_on("form-field", labels=["cc-name"])

    # verify form data in reverse (newer options are at the top)
    for idx in range(1, 3):
        autofill_popup.select_nth_element(idx)
        credit_card_autofill.verify_credit_card_form_data(sample_data[idx - 1])
        credit_card_autofill.click_on("form-field", labels=["cc-name"])
        autofill_popup.click_clear_form_option()
