import pytest
import logging
import json

from time import sleep

from selenium.webdriver import Firefox
# from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation
from modules.browser_object_autofill_popup import AutofillPopup
from modules.classes.autofill_base import AutofillAddressBase

from modules.page_object import AddressFill, AboutPrefs

from modules.util import Utilities, BrowserActions

countries = ["CA", "US"]


@pytest.mark.parametrize("country_code", countries)
def test_private_browsing_form_autofill(driver: Firefox, country_code: str):
    # instantiate objects
    Navigation(driver).open()
    address_fill_obj = AddressFill(driver).open()
    autofill_popup_obj = AutofillPopup(driver, category="privacy")
    about_prefs_obj = AboutPrefs(driver)
    util = Utilities()
    browser_action_obj = BrowserActions(driver)

    # fill data in the regular browser
    autofill_sample_data = util.fake_autofill_data(country_code)
    address_fill_obj.save_information_basic(autofill_sample_data)
    autofill_popup_obj.press_doorhanger_save()

    # open in the private browser


    # double click the name
    address_fill_obj.double_click("form-field", "name")
    with driver.context(driver.CONTEXT_CHROME):
        autofill_popup_obj.get_element("autofill-panel").click()

        panel_option = autofill_popup_obj.get_element("autofill-panel-item")
        extracted_data = panel_option.get_attribute('ac-value')
        logging.info(f"Extracted data: {extracted_data}")

        extracted_data_as_obj = json.loads(extracted_data)
        assert extracted_data_as_obj["primary"] == autofill_sample_data.name

        panel_option.click()

    # double click the field to get clear panel
    address_fill_obj.double_click("form-field", "name")
    address_fill_obj.click_clear()

    # verify empty data after clearing
    empty_autofill_data = AutofillAddressBase()
    address_fill_obj.verify_field_data(empty_autofill_data)

    # go back to normal firefox

    # verify no items in the about_prefs
    about_prefs_obj.open()
    iframe_address_popup = about_prefs_obj.press_button_get_popup_dialog_iframe(
        "Saved addresses"
    )
    browser_action_obj.switch_to_iframe_context(iframe_address_popup)

    sleep(10)
