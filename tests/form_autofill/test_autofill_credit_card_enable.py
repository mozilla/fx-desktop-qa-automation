import pytest
from selenium.webdriver import Firefox

from modules.browser_object import CreditCardPopup, Navigation
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs
from modules.page_object_autofill_credit_card import CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122388"


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

    new_credit_card_fill_obj.double_click("form-field", labels=["cc-name"])
    new_autofill_popup_obj.verify_no_popup_panel()
