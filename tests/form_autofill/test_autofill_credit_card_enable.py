import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object import AboutPrefs, CreditCardFill


@pytest.fixture()
def test_case():
    return "122388"


@pytest.fixture()
def prefs_category():
    return "passwordsAutofill"


def test_enable_disable_form_autofill_cc(
    driver: Firefox,
    about_prefs: AboutPrefs,
    autofill_popup: AutofillPopup,
    credit_card_autofill: CreditCardFill,
):
    """
    C122388, tests that after saving cc information and toggling the autofill credit
    cards box the dropdown does not appear.

    Arguments:
        about_prefs: AboutPrefs instance
        autofill_popup: AutofillPopup instance
        credit_card_autofill: CreditCardFill instance
    """

    # open credit card autofill page
    credit_card_autofill.open()

    # scroll to first form field
    credit_card_autofill.scroll_to_form_field()

    # create fake data, fill it in and press submit and save on the door hanger
    credit_card_autofill.fill_and_save()

    # navigate to prefs
    about_prefs.open()

    # toggle autofill cc option
    about_prefs.click_on("save-and-fill-payment-methods")

    # open credit card autofill page and select field
    credit_card_autofill.open()

    # scroll to first form field
    credit_card_autofill.scroll_to_form_field()

    credit_card_autofill.double_click("form-field", labels=["cc-name"])

    # make sure autofill dropdown does not appear
    autofill_popup.ensure_autofill_dropdown_not_visible()
