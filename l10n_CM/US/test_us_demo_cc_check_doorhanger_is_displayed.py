import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2889441"


def test_us_demo_cc_check_doorhanger_is_displayed(driver: Firefox):
    """
    C122393, ensures that the doorhanger is displayed after filling credit card info
    """

    # instantiate objects
    autofill_popup_obj = AutofillPopup(driver)
    util = Utilities()

    # navigate to page
    credit_card_fill_obj = CreditCardFill(driver).open()

    # fill data
    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_fill_obj.fill_credit_card_info(credit_card_sample_data)

    # check if an element from the doorhanger is visible
    autofill_popup_obj.element_visible("doorhanger-save-button")
