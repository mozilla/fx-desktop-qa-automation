import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object import AboutPrefs, CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122392"


@pytest.fixture()
def prefs_category():
    return "passwordsAutofill"


def test_autofill_credit_card_door_hanger(
    driver: Firefox,
    about_prefs: AboutPrefs,
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

    # scroll to first form field
    credit_card_autofill.scroll_to_form_field()

    # fill data
    credit_card_autofill.fill_and_save(door_hanger=False)

    # press the arrow
    autofill_popup.click_doorhanger_button("dropdown")
    autofill_popup.click_doorhanger_button("dropdown-never-save-cards")

    # ensure that the checked attribute is off
    about_prefs.open()
    about_prefs.element_does_not_have_attribute(
        "save-and-fill-payment-methods", "checked"
    )
