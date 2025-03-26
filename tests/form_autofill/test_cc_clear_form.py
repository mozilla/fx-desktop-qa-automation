import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122581"


def test_clear_form_credit_card(
    driver: Firefox,
    autofill_popup: AutofillPopup,
    credit_card_autofill: CreditCardFill,
    util: Utilities,
):
    """
    C122581, Test clear form credit card

    Arguments:
        autofill_popup: AutofillPopup instance
        credit_card_autofill: CreditCardFill instance
        util: Utilities instance
    """
    credit_card_autofill.open()

    # create fake data, fill it in and press submit and save on the doorhanger
    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_autofill.fill_credit_card_info(credit_card_sample_data)
    autofill_popup.click_doorhanger_button("save")

    # Open dropdown, select first option, clear autofill form and verify autofill is displayed
    credit_card_autofill.get_element("form-field", labels=["cc-name"]).click()
    autofill_popup.click_autofill_form_option()
    credit_card_autofill.get_element("form-field", labels=["cc-name"]).click()
    autofill_popup.click_clear_form_option()
    autofill_popup.verify_autofill_displayed()
