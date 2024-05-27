import logging
from time import sleep

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import CreditCardPopup, Navigation
from modules.browser_object_autofill_popup import AutofillPopup

# from modules.page_object import AboutPrefs
from modules.page_object_autofill_credit_card import CreditCardFill
from modules.util import Utilities


def test_autofill_update_credit_card(driver: Firefox):
    """
    C122406, updates the name of the credit card holder and ensure no new profile is created and data is saved correctly
    """
    nav = Navigation(driver)
    util = Utilities()

    nav.open()
    credit_card_fill_obj = CreditCardFill(driver).open()
    autofill_popup_obj = AutofillPopup(driver)
    credit_card_popoup_obj = CreditCardPopup(driver)

    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_fill_obj.fill_credit_card_info(credit_card_sample_data)
    autofill_popup_obj.press_doorhanger_save()
    credit_card_fill_obj.press_autofill_panel(credit_card_popoup_obj)

    new_cc_name = util.fake_credit_card_data().name
    credit_card_sample_data.name = new_cc_name

    credit_card_fill_obj.verify_updated_information(
        credit_card_popoup_obj,
        autofill_popup_obj,
        credit_card_sample_data,
        "cc-name",
        credit_card_sample_data.name,
    )

    # new_cc_number = util.fake_credit_card_data().card_number
    # credit_card_sample_data.card_number = new_cc_number

    # credit_card_fill_obj.verify_updated_information(credit_card_popoup_obj,
    #                                                 autofill_popup_obj,
    #                                                 credit_card_sample_data,
    #                                                 "cc-number",
    #                                                 credit_card_sample_data.card_number)
