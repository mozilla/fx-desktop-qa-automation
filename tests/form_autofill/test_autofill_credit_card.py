from selenium.webdriver import Firefox

from modules.browser_object import CreditCardPopup, Navigation
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs
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


def test_enable_disable_form_autofill_cc(driver: Firefox):
    """
    C122388, tests that after saving cc information and toggling the autofill credit cards box the dropdown does not appear.
    """
    nav = Navigation(driver)
    util = Utilities()

    nav.open()
    credit_card_fill_obj = CreditCardFill(driver).open()
    new_autofill_popup = AutofillPopup(driver)

    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_fill_obj.fill_credit_card_info(credit_card_sample_data)
    new_autofill_popup.press_doorhanger_save()

    about_prefs = AboutPrefs(driver, category="privacy").open()
    about_prefs.get_element("save-and-fill-payment-methods").click()

    new_credit_card_fill_obj = CreditCardFill(driver).open()
    new_autofill_popup_obj = CreditCardPopup(driver)

    new_credit_card_fill_obj.double_click("form-field", "cc-name")
    new_autofill_popup_obj.verify_no_popup_panel()
