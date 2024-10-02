import logging

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122361"


countries = ["CA", "US"]


@pytest.mark.parametrize("country_code", countries)
def test_telephone_attribute_autofill(driver: Firefox, country_code: str):
    """
    C122361, ensures that telephone numbers are autofilled
    """
    # instantiate objects
    Navigation(driver).open()
    address_fill_obj = AddressFill(driver).open()
    autofill_popup_obj = AutofillPopup(driver)
    util = Utilities()

    # create fake data, fill it in and press submit and save on the doorhanger
    autofill_sample_data = util.fake_autofill_data(country_code)
    address_fill_obj.save_information_basic(autofill_sample_data)
    autofill_popup_obj.click_doorhanger_button("save")

    # double click telephone attribute
    address_fill_obj.click_on("form-field", labels=["tel"])
    address_fill_obj.click_on("form-field", labels=["tel"])
    logging.info(f"The generated phone number: {autofill_sample_data.telephone}")
    first_item = autofill_popup_obj.get_nth_element("1")

    # get relevant fields
    autofill_popup_obj.hover(first_item)
    actual_value = autofill_popup_obj.get_primary_value(first_item)
    normalized_number = util.normalize_phone_number(actual_value)
    original_number = util.normalize_phone_number(autofill_sample_data.telephone)

    logging.info(f"Original: {actual_value}, Normalized: {normalized_number}")
    logging.info(
        f"Original: {autofill_sample_data.telephone}, Normalized: {original_number}"
    )

    # verify
    assert normalized_number == original_number
