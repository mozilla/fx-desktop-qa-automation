import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.browser_object_navigation import Navigation
from modules.page_object_autofill_test_basic import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122574"


countries = ["CA", "US"]


@pytest.mark.parametrize("country_code", countries)
def test_clear_form(driver: Firefox, country_code: str):
    """
    C122574, test clear autofill form
    """
    # instantiate objects
    Navigation(driver).open()
    address_autofill = AddressFill(driver).open()
    address_autofill_popup = AutofillPopup(driver)
    util = Utilities()

    # create fake data, fill it in and press submit and save on the doorhanger
    autofill_sample_data = util.fake_autofill_data(country_code)
    address_autofill.save_information_basic(autofill_sample_data)
    address_autofill_popup.click_doorhanger_button("save")

    # creating new objects to prevent stale webelements
    new_address_autofill = AddressFill(driver).open()

    # Open dropdown and select first option and clear autofill form
    new_address_autofill.double_click("form-field", labels=["name"])
    address_autofill_popup.click_autofill_form_option()
    new_address_autofill.click("form-field", labels=["name"])
    # Verify that the form autofill suggestions are displayed.
    address_autofill_popup.verify_element_displayed("select-form-option")
