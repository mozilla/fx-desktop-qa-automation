from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import CreditCardPopup, Navigation
from modules.page_object_autofill_credit_card import CreditCardFill

indices = [1, 2]


@pytest.mark.parametrize("index", indices)
def test_form_autofill_suggestions(driver: Firefox, index: int):
    nav = Navigation(driver)
    # util = Utilities()

    nav.open()
    credit_card_fill_obj = CreditCardFill(driver).open()
    # autofill_popup_obj = AutofillPopup(driver)
    credit_card_popoup_obj = CreditCardPopup(driver)

    # sample_data_1 = credit_card_fill_obj.fake_and_fill(util, autofill_popup_obj)
    # sample_data_2 = credit_card_fill_obj.fake_and_fill(util, autofill_popup_obj)

    credit_card_fill_obj.double_click("form-field", "cc-name")
    sleep(1)

    with driver.context(driver.CONTEXT_CHROME):
        panel_item = credit_card_popoup_obj.get_element(
            "autofill-profile-option", multiple=True
        )
        for item in panel_item:
            print(item.get_attribute("ac-value"))
        # panel_item.click()

    # # verifying that the first item (top most) is the second sample data since it was saved most recently
    # credit_card_fill_obj.verify_four_fields(credit_card_popoup_obj, sample_data_2)
    # credit_card_fill_obj.get_element("form-button", labels=["reset"]).click()
    # credit_card_fill_obj.double_click("form-field", "cc-name")

    # with driver.context(driver.CONTEXT_CHROME):
    #     panel_item = credit_card_popoup_obj.get_element("autofill-profile-option")
    #     panel_item.click()

    #     item2 = autofill_popup_obj.get_nth_element(2)
    #     item2.click()

    # # verifying that the second item (bottom most) is the first sampel data since it was saved least recently
    # print(sample_data_1)
    # credit_card_fill_obj.verify_four_fields(credit_card_popoup_obj, sample_data_1)
