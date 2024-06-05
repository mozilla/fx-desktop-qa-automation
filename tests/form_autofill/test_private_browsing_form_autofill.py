from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AddressFill
from modules.util import Utilities

countries = ["CA", "US"]


@pytest.mark.parametrize("country_code", countries)
def test_private_browsing_form_autofill(driver: Firefox, country_code: str):
    # instantiate objects
    Navigation(driver).open()
    address_fill_obj = AddressFill(driver).open()
    autofill_popup_obj = AutofillPopup(driver)
    util = Utilities()

    address_fill_obj.perform_key_combo(Keys.COMMAND, 't')

    # TODO: open the browser in incognito mode
    # autofill_sample_data = util.fake_autofill_data(country_code)
    # address_fill_obj.save_information_basic(autofill_sample_data)
    # autofill_popup_obj.press_doorhanger_save()

    # # double click the name
    # address_fill_obj.double_click("form-field", "name")
    # with driver.context(driver.CONTEXT_CHROME):
    #     autofill_popup_obj.get_element("autofill-panel").click()

    sleep(5)
