from selenium.webdriver import Firefox

from modules.browser_object import CreditCardPopup, Navigation
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill_credit_card import CreditCardFill
from modules.util import Utilities


def test_autofill_credit_card(driver: Firefox):
    """
    C122405, tests that after filling autofill and disabling cc info it appears in panel
    """
    nav = Navigation(driver)
    util = Utilities()

    nav.open()
    ccf = CreditCardFill(driver).open()
    afp = AutofillPopup(driver)
    ccp = CreditCardPopup(driver)

    credit_card_sample_data = util.fake_credit_card_data()
    ccf.fill_credit_card_info(credit_card_sample_data)
    afp.press_doorhanger_save()

    ccf.verify_all_fields(ccp)

def test_autofill_four_fields(driver: Firefox):
    nav = Navigation(driver)
    util = Utilities()

    nav.open()
    ccf = CreditCardFill(driver).open()
    afp = AutofillPopup(driver)
    ccp = CreditCardPopup(driver)

    credit_card_sample_data = util.fake_credit_card_data()
    ccf.fill_credit_card_info(credit_card_sample_data)
    afp.press_doorhanger_save()

    ccf.verify_four_fields(ccp, credit_card_sample_data)