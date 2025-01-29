import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutConfig
from modules.page_object_autofill import CreditCardFill
from modules.util import Utilities

regions = ["US", "CA", "DE", "FR"]


@pytest.fixture()
def test_case():
    return "2889441"


@pytest.mark.parametrize("region", regions)
def test_cc_check_door_hanger_is_displayed(driver: Firefox, region: str):
    """
    C2889441 - Ensures that the door hanger is displayed after filling credit card info
    """

    # Instantiate objects
    autofill_popup_obj = AutofillPopup(driver)
    credit_card_fill_obj = CreditCardFill(driver)
    util = Utilities()
    about_config = AboutConfig(driver)

    # Change pref value of region
    about_config.change_config_value("browser.search.region", region)

    # Navigate to page
    credit_card_fill_obj.open()

    # Fill data
    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_fill_obj.fill_credit_card_info(credit_card_sample_data)

    # Check if an element from the door hanger is visible
    autofill_popup_obj.element_visible("doorhanger-save-button")
