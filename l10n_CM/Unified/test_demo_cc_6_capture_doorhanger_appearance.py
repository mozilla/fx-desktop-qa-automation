import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import CreditCardFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2889441"


def test_cc_check_door_hanger_is_displayed(
    driver: Firefox,
    region: str,
    util: Utilities,
    autofill_popup: AutofillPopup,
    credit_card_fill_obj: CreditCardFill,
):
    """
    C2889441 - Ensures that the door hanger is displayed after filling credit card info
    """
    # Navigate to page
    credit_card_fill_obj.open()

    # Fill data. Don't click save in doorhanger
    credit_card_fill_obj.fill_and_save(util, autofill_popup, door_hanger=False)

    # Check if an element from the door hanger is visible
    autofill_popup.element_visible("doorhanger-save-button")
