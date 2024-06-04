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
    credit_card_fill_obj = CreditCardFill(driver).open()
    autofill_popup_obj = AutofillPopup(driver)
    credit_card_popup_obj = CreditCardPopup(driver)

    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_fill_obj.fill_credit_card_info(credit_card_sample_data)
    autofill_popup_obj.press_doorhanger_save()

    credit_card_fill_obj.verify_all_fields(credit_card_popup_obj)


def test_autofill_four_fields(driver: Firefox):
    """
    C122404, tests that the form fields are filled corrected after saving a profile.
    """
    nav = Navigation(driver)
    util = Utilities()

    nav.open()
    credit_card_fill_obj = CreditCardFill(driver).open()
    autofill_popup_obj = AutofillPopup(driver)
    credit_card_popup_obj = CreditCardPopup(driver)

    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_fill_obj.fill_credit_card_info(credit_card_sample_data)
    autofill_popup_obj.press_doorhanger_save()

    credit_card_fill_obj.verify_four_fields(
        credit_card_popup_obj, credit_card_sample_data
    )

def test_enable_disable_form_autofill_cc(driver: Firefox):
    """
    C122388, tests that after saving cc information and toggling the autofill credit
    cards box the dropdown does not appear.
    """
    nav = Navigation(driver)
    util = Utilities()

    nav.open()
    credit_card_fill_obj = CreditCardFill(driver).open()
    autofill_popup_obj = AutofillPopup(driver)

    credit_card_fill_obj.fake_and_fill(util, autofill_popup_obj)

    about_prefs = AboutPrefs(driver, category="privacy").open()
    about_prefs.get_element("save-and-fill-payment-methods").click()

    new_credit_card_fill_obj = CreditCardFill(driver).open()
    new_autofill_popup_obj = CreditCardPopup(driver)

    new_credit_card_fill_obj.double_click("form-field", "cc-name")
    new_autofill_popup_obj.verify_no_popup_panel()
