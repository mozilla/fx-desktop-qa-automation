import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs
from modules.page_object_autofill import CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122388"


def test_enable_disable_form_autofill_cc(
    driver: Firefox,
    about_prefs_privacy: AboutPrefs,
    autofill_popup: AutofillPopup,
    credit_card_autofill: CreditCardFill,
    util: Utilities,
):
    """
    C122388, tests that after saving cc information and toggling the autofill credit
    cards box the dropdown does not appear.

    Arguments:
        about_prefs_privacy: AboutPrefs instance (privacy category)
        autofill_popup: AutofillPopup instance
        credit_card_autofill: CreditCardFill instance
        util: Utilities instance
    """

    # open credit card autofill page
    credit_card_autofill.open()

    # create fake data, fill it in and press submit and save on the door hanger
    credit_card_autofill.fill_and_save()

    # navigate to prefs
    about_prefs_privacy.open()

    # toggle autofill cc option
    about_prefs_privacy.get_element("save-and-fill-payment-methods").click()

    # open credit card autofill page and select field
    credit_card_autofill.open()
    credit_card_autofill.double_click("form-field", labels=["cc-name"])

    # make sure autofill dropdown does not appear
    autofill_popup.ensure_autofill_dropdown_not_visible()
