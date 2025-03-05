import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122405"


def test_autofill_credit_card(driver: Firefox):
    """
    C122405, tests that after filling autofill and disabling cc info it appears in panel
    """
    util = Utilities()

    credit_card_fill_obj = CreditCardFill(driver).open()
    autofill_popup = AutofillPopup(driver)

    credit_card_data = util.fake_credit_card_data()
    credit_card_fill_obj.fill_credit_card_info(credit_card_data)
    autofill_popup.click_doorhanger_button("save")

    credit_card_fill_obj.verify_autofill_dropdown_credit_card(autofill_popup_obj)
