import platform

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122581"


@pytest.mark.xfail(platform.system() == "Linux", reason="Autofill Linux instability")
def test_clear_form_credit_card(driver: Firefox):
    """
    C122581, Test clear form credit card
    """
    # instantiate objects
    credit_card_autofill = CreditCardFill(driver).open()
    autofill_popup = AutofillPopup(driver)
    util = Utilities()

    # create fake data, fill it in and press submit and save on the doorhanger
    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_autofill.fill_credit_card_info(credit_card_sample_data)
    autofill_popup.click_doorhanger_button("save")

    # creating new objects to prevent stale webelements
    new_credit_card_autofill = CreditCardFill(driver).open()

    # Open dropdown, select first option, clear autofill form and verify autofill is displayed
    new_credit_card_autofill.get_element("form-field", labels=["cc-name"]).click()
    autofill_popup.click_autofill_form_option()
    new_credit_card_autofill.get_element("form-field", labels=["cc-name"]).click()
    autofill_popup.click_clear_form_option()
    autofill_popup.verify_autofill_displayed()
