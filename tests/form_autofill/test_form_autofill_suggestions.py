import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object_autofill import CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122401"


def test_form_autofill_suggestions(driver: Firefox):
    """
    C122401, checks that the corresponding autofill suggestion autofills the fields correctly
    """
    # instantiate objects
    util = Utilities()

    credit_card_fill_obj = CreditCardFill(driver).open()
    autofill_popup_obj = AutofillPopup(driver)

    # create fake data, two profiles
    sample_data = [
        credit_card_fill_obj.fake_and_fill(util, autofill_popup_obj) for _ in range(2)
    ]
    # reverse data list to match form options
    sample_data.reverse()

    # press the corresponding option (according to the parameter)
    credit_card_fill_obj.click_on("form-field", labels=["cc-name"])

    # verify form data in reverse (newer options are at the top)
    for idx in range(1, 3):
        autofill_popup_obj.select_nth_element(idx)
        credit_card_fill_obj.verify_credit_card_form_data(sample_data[idx - 1])
        credit_card_fill_obj.click_on("form-field", labels=["cc-name"])
        autofill_popup_obj.click_clear_form_option()
