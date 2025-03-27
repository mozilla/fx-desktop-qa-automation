import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs
from modules.page_object_autofill import CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122392"


def test_autofill_credit_card_door_hanger(
    driver: Firefox,
    about_prefs_privacy: AboutPrefs,
    autofill_popup: AutofillPopup,
    credit_card_autofill: CreditCardFill,
    util: Utilities,
):
    """
    C122392, ensures that pressing not now > never save cards toggles off the setting

    Arguments:
        about_prefs_privacy: AboutPrefs instance (privacy category)
        autofill_popup: AutofillPopup instance
        credit_card_autofill: CreditCardFill instance
        util: Utilities instance
    """
    # navigate to page
    credit_card_autofill.open()

    # fill data
    credit_card_autofill.fill_and_save(util, autofill_popup, door_hanger=False)

    # press the arrow
    autofill_popup.click_doorhanger_button("dropdown")
    autofill_popup.click_doorhanger_button("dropdown-never-save-cards")

    # ensure that the checked attribute is off
    about_prefs_privacy.open()
    payment_checkbox = about_prefs_privacy.get_element("save-and-fill-payment-methods")
    checked_attr = payment_checkbox.get_attribute("checked")
    assert checked_attr is None
