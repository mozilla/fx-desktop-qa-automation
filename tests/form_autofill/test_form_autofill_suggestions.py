import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup, CreditCardPopup, Navigation
from modules.page_object_autofill_credit_card import CreditCardFill
from modules.util import Utilities

indices = ["1", "2"]


@pytest.mark.parametrize("index", indices)
def test_form_autofill_suggestions(driver: Firefox, index: str):
    nav = Navigation(driver)
    util = Utilities()

    nav.open()
    credit_card_fill_obj = CreditCardFill(driver).open()
    autofill_popup_obj = AutofillPopup(driver)
    credit_card_popoup_obj = CreditCardPopup(driver)

    sample_data_1 = credit_card_fill_obj.fake_and_fill(util, autofill_popup_obj)
    sample_data_2 = credit_card_fill_obj.fake_and_fill(util, autofill_popup_obj)

    credit_card_fill_obj.double_click("form-field", "cc-name")

    with driver.context(driver.CONTEXT_CHROME):
        item1 = autofill_popup_obj.get_nth_element(index)
        item1.click()

    credit_card_fill_obj.verify_four_fields(
        credit_card_popoup_obj, sample_data_2 if index == "1" else sample_data_1
    )
