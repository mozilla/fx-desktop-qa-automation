import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122404"


def test_autofill_four_fields(
    driver: Firefox,
    autofill_popup: AutofillPopup,
    credit_card_autofill: CreditCardFill,
    util: Utilities,
):
    """
    C122404, tests that the form fields are filled corrected after saving a profile.

    Arguments:
        autofill_popup: AutofillPopup instance
        credit_card_autofill: CreditCardFill instance
        util: Utilities instance
    """
    credit_card_autofill.open()

    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_autofill.fill_credit_card_info(credit_card_sample_data)
    autofill_popup.click_doorhanger_button("save")

    credit_card_autofill.press_autofill_panel(autofill_popup)
    credit_card_autofill.verify_credit_card_form_data(credit_card_sample_data)
