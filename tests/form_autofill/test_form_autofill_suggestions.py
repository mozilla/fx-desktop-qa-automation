import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup, CreditCardPopup, Navigation
from modules.page_object_autofill_credit_card import CreditCardFill
from modules.util import Utilities

indices = ["1", "2"]


@pytest.mark.parametrize("index", indices)
def test_form_autofill_suggestions(driver: Firefox, index: str):
    """
    C122401, checks that the corresponding autofill suggestion autofills the fields correctly
    """
    # instantiate objects
    nav = Navigation(driver)
    util = Utilities()

    nav.open()
    credit_card_fill_obj = CreditCardFill(driver).open()
    autofill_popup_obj = AutofillPopup(driver)
    credit_card_popoup_obj = CreditCardPopup(driver)

    # create fake data, two profiles
    sample_data_1 = credit_card_fill_obj.fake_and_fill(util, autofill_popup_obj)
    sample_data_2 = credit_card_fill_obj.fake_and_fill(util, autofill_popup_obj)

    # press the corresponding option (according to the parameter)
    credit_card_fill_obj.double_click("form-field", "cc-name")
    with driver.context(driver.CONTEXT_CHROME):
        panel_option = autofill_popup_obj.get_nth_element(index)
        panel_option.click()

    # verify information based, verify based on second object if we are verifying first option (this is the newer option) and
    # vice versa
    credit_card_fill_obj.verify_four_fields(
        credit_card_popoup_obj, sample_data_2 if index == "1" else sample_data_1
    )
