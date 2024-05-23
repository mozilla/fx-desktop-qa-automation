import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AddressFill
from modules.util import Utilities

countries = ["CA", "US"]


@pytest.mark.parametrize("country_code", countries)
def test_telephone_attribute_autofill(driver: Firefox, country_code: str):
    """
    C122361
    """
    # instantiate objects
    Navigation(driver).open()
    address_fill_obj = AddressFill(driver).open()
    autofill_popup_obj = AutofillPopup(driver)
    util = Utilities()

    # create fake data, fill it in and press submit and save on the doorhanger
    autofill_sample_data = util.fake_autofill_data(country_code)
    address_fill_obj.save_information_basic(autofill_sample_data)
    autofill_popup_obj.press_doorhanger_save()

    # double click telephone attribute
    address_fill_obj.double_click("form-field", "tel")
    first_item = autofill_popup_obj.get_nth_element("1")

    # get relevant fields
    autofill_popup_obj.hover_over_element(first_item)
    actual_value = autofill_popup_obj.get_primary_value(first_item)
    normalized_number = address_fill_obj.normalize_phone_number(actual_value)
    original_number = address_fill_obj.normalize_phone_number(
        autofill_sample_data.telephone
    )

    # verify
    assert normalized_number == original_number
