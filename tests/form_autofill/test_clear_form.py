import time

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.browser_object_navigation import Navigation
from modules.page_object_autofill_test_basic import AddressFill
from modules.util import Utilities
from selenium.webdriver.support import expected_conditions as EC

countries = ["CA", "US"]


@pytest.mark.parametrize("country_code", countries)
def test_clear_form(driver: Firefox, country_code: str):
    """
    C122574, test clear autofill form
    """
    # instantiate objects
    Navigation(driver).open()
    af = AddressFill(driver).open()
    afp = AutofillPopup(driver)
    util = Utilities()

    # create fake data, fill it in and press submit and save on the doorhanger
    autofill_sample_data = util.fake_autofill_data(country_code)
    af.save_information_basic(autofill_sample_data)
    afp.press_doorhanger_save()

    # creating new objects to prevent stale webelements
    new_af = AddressFill(driver).open()

    # Open dropdown and select first option and clear autofill form
    new_af.double_click("form-field", "name")
    new_af.click_address()
    new_af.click("form-field", "name")
    new_af.click_clear()
