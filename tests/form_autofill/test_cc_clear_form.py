import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.browser_object_navigation import Navigation
from modules.page_object_autofill_credit_card import CreditCardFill
from modules.util import Utilities


@pytest.mark.unstable
def test_clear_form_credit_card(driver: Firefox):
    """
    C122581, Test clear form credit card
    """
    # instantiate objects
    Navigation(driver).open()
    credit_card_autofill = CreditCardFill(driver).open()
    autofill_popup = AutofillPopup(driver)
    util = Utilities()

    # create fake data, fill it in and press submit and save on the doorhanger
    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_autofill.fill_credit_card_info(credit_card_sample_data)
    autofill_popup.press_doorhanger_save()

    # creating new objects to prevent stale webelements
    new_credit_card_autofill = CreditCardFill(driver).open()

    # Open dropdown, select first option, clear autofill form and verify autofill is displayed
    new_credit_card_autofill.get_element("form-field", labels=["cc-name"]).click()
    autofill_popup.click_credit_card()
    new_credit_card_autofill.get_element("form-field", labels=["cc-name"]).click()
    autofill_popup.click_clear_credit_card()
    autofill_popup.verify_autofill_displayed()
