import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.browser_object_navigation import Navigation
from modules.page_object import AboutPrefs
from modules.page_object_autofill_credit_card import CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122392"


def test_autofill_credit_card_doorhanger(driver: Firefox):
    """
    C122392, ensures that pressing not now > never save cards toggles off the setting
    """
    # instantiate objects
    nav = Navigation(driver)
    about_prefs_obj = AboutPrefs(driver, category="privacy")
    autofill_popup_obj = AutofillPopup(driver)
    util = Utilities()

    # navigate to page
    nav.open()
    credit_card_fill_obj = CreditCardFill(driver).open()

    # fill data
    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_fill_obj.fill_credit_card_info(credit_card_sample_data)

    # press the arrow
    autofill_popup_obj.click_doorhanger_button("dropdown")
    autofill_popup_obj.click_doorhanger_button("dropdown-never-save-cards")

    # ensure that the checked attribute is off
    about_prefs_obj.open()
    payment_checkbox = about_prefs_obj.get_element("save-and-fill-payment-methods")
    checked_attr = payment_checkbox.get_attribute("checked")
    assert checked_attr is None
