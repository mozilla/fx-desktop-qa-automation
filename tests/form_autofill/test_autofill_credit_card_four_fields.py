import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122404"


def test_autofill_four_fields(driver: Firefox):
    """
    C122404, tests that the form fields are filled corrected after saving a profile.
    """
    util = Utilities()

    credit_card_fill_obj = CreditCardFill(driver).open()
    autofill_popup_obj = AutofillPopup(driver)

    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_fill_obj.fill_credit_card_info(credit_card_sample_data)
    autofill_popup_obj.click_doorhanger_button("save")

    credit_card_fill_obj.press_autofill_panel(autofill_popup_obj)
    credit_card_fill_obj.verify_credit_card_form_data(credit_card_sample_data)
